import yaml
import os
import stat
import re
import boto3
import fabric

from datetime import datetime
from functools import partial

from cement import Controller, ex
from cement.utils import fs
from cement.utils import shell

from ..core.utils import environment_names, job_names, find_nearest_root
from ..core.environments.stack_collection import StackCollection
from ..core.clusters.cluster_booter import ClusterBooter
from ..core.clusters.cluster_instance import ClusterInstance
from .arguments import profile as profile_arg
from .arguments import cluster_id as cluster_id_arg
from .arguments import ssh_key_location as ssh_key_location_arg


class Clusters(Controller):

    class Meta:
        label = 'clusters'
        stacked_type = 'nested'
        stacked_on = 'base'
        help = 'create and manage EMR clusters'

    @ex(
        help='list clusters',
        arguments=[
            (['-a', '--all'], {
                'help': 'Filter list to all the clusters intead of just ones you created',
                'action': 'store_true'
            }),
            (['-s', '--state'], {
                'help': 'By default we only show WAITING, RUNNING clusters pass in -s multiple times for multiple states',
                'action': 'append',
                'choices': ['STARTING', 'BOOTSTRAPPING', 'RUNNING', 'WAITING', 'TERMINATING', 'TERMINATED', 'TERMINATED_WITH_ERRORS'],
                'default': ['WAITING', 'RUNNING']
            }),
            profile_arg()
        ]
    )
    def list(self):
        profile = self.app.pargs.profile
        states = self.app.pargs.state
        allclusters = self.app.pargs.all

        session = boto3.session.Session(profile_name=profile)
        client = session.client('emr')
        paginator = client.get_paginator('list_clusters')

        table = self.app.db.table('users')
        user_id = table.all()[0]['id']

        def mine(cluster):
            for tag in cluster['Tags']:
                if tag['Key'] == 'user_id' and tag['Value'] == user_id:
                    return True
            return False

        clusters = []
        for response in paginator.paginate(ClusterStates=states):
            clusters = [*response['Clusters'], *clusters]

        clusters = [client.describe_cluster(ClusterId=cluster['Id'])[
            'Cluster'] for cluster in clusters]

        if not allclusters:
            clusters = [cluster for cluster in clusters if mine(cluster)]

        for cluster in clusters:
            self.app.log.info(yaml.dump(cluster))

    @ex(
        help='Install Dependencies from config file',
        arguments=[
            cluster_id_arg(),
            ssh_key_location_arg(),
            profile_arg(),
            (['-f', '--config-file'], {
                'help': 'Path to the cluster config file (example: ./jobs/config/clusters/dev/config.yml)',
                'required': True
            })
        ]
    )
    def install(self):

        cluster_id = self.app.pargs.cluster_id
        profile = self.app.pargs.profile
        ssh_key = self.app.pargs.ssh_key
        config_file = self.app.pargs.config_file
        log = self.app.log

        session = boto3.session.Session(profile_name=profile)
        client = session.client('emr')
        response = client.describe_cluster(ClusterId=cluster_id)

        paginator = client.get_paginator('list_instances')
        response_iterator = paginator.paginate(ClusterId=cluster_id)

        # try:
        cluster_conf = open(config_file, "r").read()
        pips = yaml.load(cluster_conf).get('PipInstall', [])
        # except:
        #    log.error("Sorry we couldn't find anything to pip install in your config file")
        #    return

        for response in response_iterator:
            for instance in response['Instances']:
                instance = ClusterInstance(
                    instance, {"key_filename": [ssh_key]})
                log.info("\nInstalling dependencies on %s" %
                         instance.public_dns_name)
                resp = instance.run_cmd(
                    "sudo /usr/bin/python3 -m pip install %s" % (" ".join(pips)))
                log.info(resp)

    @ex(
        help='Run a command on the remote cluster',
        arguments=[
            (['-r', '--run-cmd'], {
                'help': 'A string representing the command you want to run',
                'required': True
            }),
            (['-m', '--master-only'], {
                'help': 'Run only on master',
                'action': 'store_true'
            }),
            profile_arg(),
            cluster_id_arg(),
            ssh_key_location_arg()
        ]
    )
    def run_cmd(self):
        cluster_id = self.app.pargs.cluster_id
        profile = self.app.pargs.profile
        master_only = self.app.pargs.master_only
        ssh_key = self.app.pargs.ssh_key
        log = self.app.log

        session = boto3.session.Session(profile_name=profile)
        client = session.client('emr')
        response = client.describe_cluster(ClusterId=cluster_id)
        master_dns = response['Cluster']['MasterPublicDnsName']

        paginator = client.get_paginator('list_instances')
        response_iterator = paginator.paginate(ClusterId=cluster_id)
        instances = []
        for response in response_iterator:
            for instance in response['Instances']:
                instances.append(ClusterInstance(
                    instance, {"key_filename": [ssh_key]}))

        if master_only:
            instances = [
                instance for instance in instances if instance.public_dns_name == master_dns]

        for instance in instances:
            log.info("\nRunning command on host %s" % instance.public_dns_name)
            resp = instance.run_cmd(self.app.pargs.run_cmd)
            log.info(resp)

    @ex(
        help='Copy files from local machine to every node in the cluster',
        arguments=[
            (['-c', '--cluster-id'], {
                'help': 'Id of the cluster you want to copy files to (hint: use list to show clusters)',
                'action': 'store'
            }),
            (['-s', '--source'], {
                'help': 'What folder / file do you want to copy over to the cluster',
                'action': 'store'
            }),
            (['-d', '--dest'], {
                'help': 'destination directory or file on the cluster',
                'action': 'store',
                'default': '/home/hadoop'
            }),
            (['-k', '--ssh-key'], {
                'help': 'location of ssh key to log into cluster nodes',
                'action': 'store',
                'required': True
            }),
            (['-p', '--profile'], {
                'help': 'AWS profile',
                'action': 'store',
                'default': 'default'
            })
        ]
    )
    def copy(self):
        cluster_id = self.app.pargs.cluster_id
        profile = self.app.pargs.profile
        ssh_key = self.app.pargs.ssh_key
        source = self.app.pargs.source
        dest = self.app.pargs.dest
        log = self.app.log

        session = boto3.session.Session(profile_name=profile)
        client = session.client('emr')
        paginator = client.get_paginator('list_instances')

        response_iterator = paginator.paginate(
            ClusterId=cluster_id
        )
        instances = []
        for response in response_iterator:
            for instance in response['Instances']:
                instances.append(ClusterInstance(
                    instance, {"key_filename": [ssh_key]}))

        for instance in instances:
            log.info("\n\nCopy file or folder %s, to %s:%s" %
                     (source, instance.public_dns_name, dest))
            result = instance.syncfiles(source, dest)
            log.info(str(result))

    @ex(
        help='boot a cluster based on the cluster config',
        arguments=[
            (['-p', '--profile'], {
                'help': 'AWS profile (default: default)',
                'action': 'store',
                'default': 'default'
            }),
            (['-n', '--name'], {
                'help': 'name of the keypair to generate',
                'action': 'store',
                'required': True
            }),
            (['-d', '--dir'], {
                'help': 'directory to put key',
                'action': 'store',
                'default': os.path.join(fs.HOME_DIR, '.ssh')
            })
        ]
    )
    def create_ec2_key(self):
        profile = self.app.pargs.profile
        name = self.app.pargs.name
        directory = self.app.pargs.dir

        session = boto3.session.Session(profile_name=profile)
        client = session.client('ec2')
        names = [pair['KeyName']
                 for pair in client.describe_key_pairs().get('KeyPairs', [])]

        if name in names:
            self.app.log.fatal(
                "Key already exists please specify a different key name")
            self.app.log.info(
                "These are the keys associated with your profile")
            self.app.log.info(yaml.dump(names, default_flow_style=False))
            return

        keypair = client.create_key_pair(KeyName=name)
        fs.ensure_dir_exists(directory)

        key_location = os.path.join(
            directory, "{name}".format(name=keypair['KeyName']))

        with open(key_location, 'w') as text_file:
            text_file.write(keypair['KeyMaterial'])

        self.app.log.info("Wrote new key to %s" % (key_location))
        os.chmod(key_location, stat.S_IRUSR | stat.S_IWUSR)
        self.app.log.info(
            "Changed permissions to prevent other users from reading the key")

    @ex(
        help='boot a cluster based on the cluster config',
        arguments=[
            (['-p', '--profile'], {
                'help': 'AWS profile (default: default)',
                'action': 'store',
                'default': 'default'
            }),
            (['-c', '--config'], {
                'help': 'Location of cluster config on the file system',
                'action': 'store',
                'required': True
            }),
            (['-k', '--ec2-key-name'], {
                'help': 'The ssh key, required if you want to log into the machine',
                'action': 'store'
            }),
            (['-Y'], {
                'help': 'Defaults will be chosen, useful for production',
                'action': 'store_true'
            }),
        ]
    )
    def boot(self):

        ec2_key_name = self.app.pargs.ec2_key_name or None
        profile = self.app.pargs.profile
        log = self.app.log
        config_path = self.app.pargs.config
        should_prompt = not self.app.pargs.Y

        if not ec2_key_name:
            log.warning("""
            You'll likely want to be able to log in or change dependencies of this cluster. 
            Without a key that will not be possible. If this is a dev cluster, it's almost a 
            certainty that you will want to specify a key.
            
            To create a key run: 
            
                cluster_funk clusters create-ec2-key -n my-key-name

            """)
            if should_prompt:
                resp = shell.Prompt("Do you still want to create the cluster?", options=[
                                    'yes', 'no'], numbered=True)
                if resp.input == 'no':
                    log.info("({input}) selected, please try again once you have create a ec2_key".format(
                        input=resp.input))
                    return

        try:
            table = self.app.db.table('users')
            user_id = table.all()[0]['id']
        except IndexError:
            user_id = None

        if not os.path.exists(config_path):
            log.info(
                "Could not find the cluster configuration you entered.  Please specify a valid path")
            return

        config = yaml.load(open(config_path).read())
        # TODO: create a config validator maybe to help with config issues.
        config['Tags'] = config.get('Tags', {})
        config['Tags']['user_id'] = user_id
        config['Ec2KeyName'] = self.app.pargs.ec2_key_name or None

        session = boto3.session.Session(profile_name=profile)

        booter = ClusterBooter(config, session)
        wait, resp = booter.boot()
        if wait:
            log.info(
                "Waiting for cluster to boot.  This can take about 10 minutes.  Feel free to grab a cup of ☕")
            wait()
            log.info("All set, cluster is fully booted.")

        table = self.app.db.table('history')
        table.insert({
            'action': 'cluster_boot',
            'resp': resp,
            'on': str(datetime.now())
        })

    @ex(
        help='given some stack information along with a job name, generate a config file',
        arguments=[
            (['-s', '--stack-prefix'], {
                'help': 'The cloudforamtion stack prefix (default: emr-spark-dev)',
                'action': 'store',
                'default': 'emr-spark'
            }),
            (['-p', '--profile'], {
                'help': 'AWS profile (default: default)',
                'action': 'store',
                'default': 'default'
            }),
            (['-j', '--job'], {
                'help': 'What job is this configuration for?',
                'action': 'store',
                'choices': job_names()
            }),
            (['-f', '--force'], {
                'help': 'Overwrite existing config if there is one',
                'action': 'store_true'
            }),
            (['-b', '--bucket'], {
                'help': 'S3 bucket used for logging and code storage',
                'action': 'store'
            }),
            (['-e', '--env'], {
                'help': 'Environment must be set',
                'action': 'store',
                'required': True,
                'choices': environment_names()
            })
        ]
    )
    def generate_config(self):
        args = self.app.pargs
        job = args.job or "unknown job"
        env = args.env or "dev"

        session = boto3.session.Session(profile_name=args.profile)
        client = session.client('cloudformation')
        stacks = StackCollection(client). \
            filter_by(StackCollection.is_cf_stack). \
            filter_by(partial(StackCollection.has_env, args.env)). \
            filter_by(partial(StackCollection.has_prefix, args.stack_prefix))

        output = stacks.output_dict()
        cluster_name = "Apache Spark for job {env}/{job}".format(
            env=env, job=job)
        # acquire latest Base AMI
        config = {
            'Name': cluster_name,
            'WorkLoadBucket': args.bucket,
            'WorkLoadPrefix': "apache_spark_for_job_{env}_{job}".format(env=env, job=job),
            'Schedule': {
                'Period': 'hourly',
                'Starting': datetime.now(),
                'Ending': datetime.now()
            },
            'Master': {
                'Instance': {
                    'Type': 'm4.large',
                    'Storage': 32
                }
            },
            'Worker': {
                'Instance': {
                    'Type': 'm4.large',
                    'Count': 1,
                    'Storage': 100,
                    'SpotCount': 0
                }
            },
            'KeepJobFlowAliveWhenNoSteps': True,
            'PipInstall': ["pandas==0.24.0"],
            'JobFlowRole': output.get('EMREc2RoleName', 'EMR_EC2_DefaultRole'),
            'ServiceRole': output.get('EMRRoleName', 'EMR_DefaultRole'),
            'AutoScalingRole': output.get('EMRAutoScalingRoleName', 'EMR_AutoScaling_DefaultRole'),
            'Ec2SubnetId': output.get('PublicSubnets', 'WARNING_INVALID_VALUE'),
            'EmrManagedMasterSecurityGroup': output.get('EmrManagedMasterSecurityGroup', 'WARNING_INVALID_VALUE'),
            'EmrManagedSlaveSecurityGroup': output.get('EmrManagedSlaveSecurityGroup', 'WARNING_INVALID_VALUE'),
            'EbsRootVolumeSize': 40,
            'AwsXrayEnabled': False,
            'ShutdownAfterInactivity': '2 hours',
            'Tags': {
                'Name': cluster_name,
                'Application': job,
                'job': job,
                'tool': 'cluster_funk',
                'Environment': env,
                'environment': env,
            }
        }

        # make sure env and job are valid!
        if env and job:
            root = find_nearest_root()
            env_config_path = os.path.join(
                root, 'jobs', job, 'config', 'clusters', env)
            config_path = os.path.join(env_config_path, "config.yml")
            fs.ensure_dir_exists(env_config_path)

            if not os.path.exists(config_path) or args.force:
                with open(config_path, "w") as text_file:
                    text_file.write(
                        yaml.dump(config, default_flow_style=False))
                self.app.log.info("Wrote a new config file too. {config_path}".format(
                    config_path=config_path))
            else:
                self.app.log.info(
                    "config already exists use -f if you really want to overwrite the existing one")

        self.app.log.info("\n%s" % yaml.dump(config, default_flow_style=False))

    @ex(
        help="Destroy the cluster given an id",
        arguments=[cluster_id_arg(), profile_arg()]
    )
    def destroy(self):
        profile = self.app.pargs.profile
        session = boto3.session.Session(profile_name=profile)
        client = session.client('emr')
        resp = client.terminate_job_flows(
            JobFlowIds=[self.app.pargs.cluster_id])
        self.app.log.info(resp)

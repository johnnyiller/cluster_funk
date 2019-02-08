import yaml
import textwrap
import hashlib

class ClusterBooter:

    def __init__(self, config, session):
        self.user_config = config
        self.emr_client = session.client('emr')
        self.s3_client = session.client('s3')
        self.bucket = config["WorkLoadBucket"]
        self.prefix = config["WorkLoadPrefix"]
        self._set_config()

    def _args_to_dict(self, **kwargs):
        return kwargs

    def _base_config(self):
        return self._args_to_dict(
            Name='placeholder',
            LogUri="placeholder",
            ReleaseLabel='emr-5.20.0',
            Instances={
                'InstanceGroups': [
                    {
                        'Name': 'MasterEMR',
                        'Market': 'ON_DEMAND',
                        'InstanceRole': 'MASTER',
                        'InstanceType': 'm1.medium',
                        'InstanceCount': 1,
                        'EbsConfiguration': {
                            'EbsBlockDeviceConfigs': [{
                                'VolumeSpecification': {
                                    'SizeInGB':32,
                                    'VolumeType':'gp2'
                                },
                                'VolumesPerInstance':1
                            }],
                            'EbsOptimized':False
                        }   
                    }, 
                    {
                        'Name': 'WorkerEMR',
                        'Market': 'ON_DEMAND',
                        'InstanceCount': 1,
                        'InstanceType': 'm1.medium',
                        'InstanceRole': 'CORE',
                        'EbsConfiguration': {
                            'EbsBlockDeviceConfigs': [{ 
                                'VolumeSpecification': {
                                    'SizeInGB':100,
                                    'VolumeType':'gp2'
                                },
                                'VolumesPerInstance':1
                            }],
                            'EbsOptimized':False
                        }
                    }
                ],
                #'Ec2KeyName': 'Dcos',
                'KeepJobFlowAliveWhenNoSteps': True,
                'TerminationProtected': False,
                'Ec2SubnetId': 'placeholder',
                'EmrManagedMasterSecurityGroup': 'placeholder',
                'EmrManagedSlaveSecurityGroup': 'placeholder'
            },
            Steps=[],
            BootstrapActions=[],
            Applications=[
                {
                    'Name': 'Spark'
                },
                {
                    'Name': 'Livy'
                },
                {
                    'Name': 'Hadoop'
                },
                {
                    'Name': 'Hive'
                }
            ],
            Configurations= [
                {
                    'Classification':'emrfs-site',
                    'Properties': {
                        "fs.s3.consistent.retryPeriodSeconds":"10",
                        "fs.s3.consistent":"true",
                        "fs.s3.consistent.retryCount":"5",
                        "fs.s3.consistent.metadata.tableName": "EmrFSMetadata"
                    }
                },
                {
                    "Classification": "spark-defaults", 
                    "Properties": {
                        "spark.yarn.appMasterEnv.SPARK_HOME": "/usr/lib/spark",
                        "spark.yarn.appMasterEnv.PYSPARK_PYTHON": "/usr/bin/python3"
                    }
                },
                {
                    "Classification": "yarn-site", 
                    "Properties": {
                        "yarn.nodemanager.vmem-check-enabled": "false"
                    }
                },
                {
                     "Classification": "spark-env",
                     "Configurations": [
                         {
                             "Classification": "export",
                             "Properties": {
                                "PYSPARK_PYTHON": "/usr/bin/python3"
                             }
                       }
                    ]
                },
                {
                    "Classification": "spark-hive-site",
                    "Properties": {
                        "hive.metastore.client.factory.class": "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
                    }
                }
            ],
            VisibleToAllUsers=True,
            JobFlowRole='place_holder',
            ServiceRole='place_holder',
            AutoScalingRole='place_holder',
            ScaleDownBehavior='TERMINATE_AT_TASK_COMPLETION',
            EbsRootVolumeSize=40
        )

    def _set_config(self):
        # the task is to mix these two configs together to get a final config.
        base = self._base_config().copy()
        user_config = self.user_config.copy()

        cluster_properties = (
            'JobFlowRole', 
            'ServiceRole', 
            'AutoScalingRole', 
            'Name', 
            'EbsRootVolumeSize'
        )

        for item in cluster_properties:
            user_config_item = user_config.get(item, None) 
            if user_config_item:
                base[item] = user_config_item
                user_config_item = None
        
        if user_config.get('Ami', None):
            base['CustomAmiId'] = user_config['Ami']

        instances = base['Instances']
        instance_properties = (
            'KeepJobFlowAliveWhenNoSteps', 
            'Ec2SubnetId', 
            'EmrManagedMasterSecurityGroup', 
            'EmrManagedSlaveSecurityGroup'
        )
        for item in instance_properties:
            user_config_item = user_config.get(item, None) 
            if user_config_item:
                instances[item] = user_config_item
                user_config_item = None

        base['Tags'] = base.get('Tags', [])
        for k, v in user_config.get('Tags',{}).items():
            base['Tags'].append({ 'Key': k, 'Value': v })

        for group in base['Instances']['InstanceGroups']:
            if group['InstanceRole'] == 'MASTER':
                group['InstanceType'] = user_config['Master']['Instance']['Type']
                for device_config in group['EbsConfiguration']['EbsBlockDeviceConfigs']:
                    device_config['VolumeSpecification']['SizeInGB'] = user_config['Master']['Instance']['Storage']

            if group['InstanceRole'] == 'CORE':
                group['InstanceCount'] = user_config['Worker']['Instance']['Count']
                group['InstanceType'] = user_config['Worker']['Instance']['Type']
                for device_config in group['EbsConfiguration']['EbsBlockDeviceConfigs']:
                    device_config['VolumeSpecification']['SizeInGB'] = user_config['Worker']['Instance']['Storage']


        base['LogUri'] = "s3n://{bucket}/{prefix}/logs".format(
            bucket=user_config["WorkLoadBucket"], 
            prefix=user_config["WorkLoadPrefix"]
        )
        if user_config['PipInstall']:
            script = self._generate_pip_script(user_config['PipInstall'])
            location = self._save_script_to_s3(script)
            base['BootstrapActions'].append({
                'Name': 'Install Python Libs',
                'ScriptBootstrapAction': {
                    'Path': location
                }
            })
        
        if user_config['AwsXrayEnabled']:
            script = self._generate_xray_script()
            location = self._save_script_to_s3(script)
            base['BootstrapActions'].append({
                'Name': 'Install AWS Xray',
                'ScriptBootstrapAction': {
                    'Path': location
                }
            })
        
        if user_config['Ec2KeyName']:
            base['Instances']['Ec2KeyName'] = user_config['Ec2KeyName']

        self.config = base

        return self.config

    def _generate_pip_script(self, pips):
        script=[
            '#!/bin/bash',
            'set -e',
            'FILE="/home/hadoop/requirements.txt"',
            'sudo /bin/cat <<EOM >$FILE'
        ]

        for pip in pips:
            script.append(pip)

        script.append('EOM')
        script.append('sudo /usr/bin/python3 -m pip install -r $FILE')
        return "\n".join(script)

    def _generate_xray_script(self):
        script = [
            '#!/bin/bash',
            'set -e',
            'curl https://s3.dualstack.us-east-1.amazonaws.com/aws-xray-assets.us-east-1/xray-daemon/aws-xray-daemon-3.x.rpm -o /home/hadoop/xray.rpm',
            'sudo yum install -y /home/hadoop/xray.rpm'
        ]
        return "\n".join(script)

    def _save_script_to_s3(self, script):
        script_bytes = script.encode('utf-8')
        file_name = hashlib.md5(script_bytes).hexdigest()
        self.s3_client.put_object(
            Body=script_bytes,
            Bucket=self.bucket, 
            Key="%s/scripts/%s.sh" % (self.prefix, file_name)
        )
        return "s3://%s/%s/scripts/%s.sh" % (self.bucket, self.prefix, file_name)
    
    def boot(self):
        response = self.emr_client.run_job_flow(**self.config)
        waiter = self.emr_client.get_waiter('cluster_running')
        def wait():
            waiter.wait(
                ClusterId=response['JobFlowId'],
                WaiterConfig={
                    'Delay': 30,
                    'MaxAttempts': 30
                }
            )
        return wait, response 

import re
import argparse
import boto3
import uuid
import os
import yaml

from cement import Controller, ex
from cement.utils import fs
from cement.utils.shell import Prompt
from tinydb import Query

from ..core.utils import find_nearest_root
from ..core.clusters.cluster_instance import ClusterInstance
from ..core.jobs.job_collection import JobCollection
from ..core.clusters.cluster_instance_collection import ClusterInstanceCollection
from ..core.clusters.emr_cluster import EmrCluster

from .arguments import profile as profile_arg
from .arguments import job_id as job_id_arg
from .arguments import job_state as job_state_arg
from .arguments import cluster_id as cluster_id_arg
from .arguments import job_name as job_name_arg
from .arguments import job_argument as job_argument_arg
from .arguments import ssh_key_location as ssh_key_location_arg
from .arguments import job_on_failure as job_on_failure_arg
from .arguments import job_on_success as job_on_success_arg

def emr_client(pargs):
    session = boto3.session.Session(profile_name=pargs.profile)
    return session.client('emr')

class Jobs(Controller):

    class Meta:
        label = 'jobs'
        stacked_type = 'nested'
        stacked_on = 'base'
        description = 'Commands for creating and submitting jobs to running clusters'
        epilog = "Usage: cluster_funk jobs generate -n my_great_new_job"
        help="Create and submit jobs to a cluster"

    @ex(
        help='Get the most recent 100 jobs from a cluster',
        arguments=[
            cluster_id_arg(),
            job_id_arg(),
            profile_arg(),
            job_state_arg() 
        ]
    )
    def list(self):
        #most_recent_cluster_id(self.app)
        client = emr_client(self.app.pargs)
        cluster_id = self.app.pargs.cluster_id
        job_id = self.app.pargs.job_id
        states = self.app.pargs.state

        jobs = JobCollection(
            client=client, 
            cluster_id=cluster_id, 
            job_id=job_id, 
            states=states
        )

        if len(jobs):
            for job in jobs.reverse():
                self.app.log.info("\n----------------------------\n%s" % (yaml.dump(job)))
        else:
            self.app.log.info("We didn't find any jobs for that cluster.  please check the cluster id")

    @ex(
        help='Bundle up a job and submit it to the running cluster',
        arguments = [
            job_name_arg(), 
            cluster_id_arg(),
            profile_arg(),
            job_argument_arg(),
            ssh_key_location_arg(),
            job_on_failure_arg()
        ]
    )
    def submit(self):
        root_path = find_nearest_root()        
        profile = self.app.pargs.profile
        cluster_id = self.app.pargs.cluster_id
        on_failure = self.app.pargs.on_failure
        name = self.app.pargs.name
        ssh_key = self.app.pargs.ssh_key
        arguments = self.app.pargs.argument
        log = self.app.log

        session = boto3.session.Session(profile_name=profile)
        client = session.client('emr')
        
        job_dir = "{root}/jobs/{name}".format(root=root_path, name=name)
        job_folder_id = str(uuid.uuid4())
        dest = "/mnt/tmp/%s" % (job_folder_id)

        log.info("Staging job run: %s" % (job_folder_id))
        
        instances = ClusterInstanceCollection(
            client=client,
            cluster_id=cluster_id,
            cluster_key=ssh_key,
            log=log
        )
        instances.syncfiles(job_dir, dest)

        log.info("Add folder to hdfs")
        instances[0].run_cmd("hadoop fs -mkdir -p /mnt/tmp")   
        instances[0].run_cmd("hadoop fs -put %s %s" % (dest, dest))
        cluster = EmrCluster(
            client=client,
            cluster_id=cluster_id,
            log=log 
        )
        job_params = {
            'job_path': dest,
            'on_failure': on_failure
        }
        if arguments:
            job_params['arguments'] = arguments

        response = cluster.submit_spark_job(**job_params)
         
        log.info(response)

    @ex(
        help='Generate a new job in the jobs directory',
        arguments = [
            job_name_arg()
        ]
    )
    def generate(self):
        root_path = find_nearest_root()        

        if not root_path:
            self.app.log.fatal("Could not find the root of the project please change directories")
            return None

        fs.ensure_dir_exists("%s/jobs" % root_path)
        job_dir = "{root}/jobs/{name}".format(root=root_path, name=self.app.pargs.name)

        if os.path.exists(job_dir):
            self.app.log.fatal("Sorry there is already a job in this directory can't overwrite")
            return None

        example_path = os.path.join(fs.abspath(__file__), os.pardir, os.pardir, "templates", "word_count")
        data = {
            "name": self.app.pargs.name
        }
        self.app.template.copy(example_path, job_dir, data)
        self.app.log.info("""
            A cluster config is not created when you generate a job, 
            please refer to the job README.md for instructions on how to generate
            a cluster config file that can be used to run jobs on EMR

            Alternatively you can type if you are familiar with the process:

            cluster_funk clusters generate-config -h 
            
        """)

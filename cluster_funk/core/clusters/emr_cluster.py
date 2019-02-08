import logging

class EmrCluster:

    def __init__(self, client, cluster_id, log=logging.Logger("cluster_funk")):
        self.cluster_id = cluster_id
        self.client = client

    def submit_spark_job(self, job_path, arguments=[], on_failure='CONTINUE'):
        base_args = [
            'spark-submit',
            '--deploy-mode',
            'client',
            '%s/main.py' % (job_path)
        ]
        for argument in arguments:
            replace_argument = argument.replace('__JOB_PATH__', job_path)
            base_args.append(replace_argument)

        return self.client.add_job_flow_steps(
            JobFlowId=self.cluster_id,
            Steps=[
                {
                    'Name': "Spark cluster_funk",
                    'ActionOnFailure': on_failure,
                    'HadoopJarStep': {
                        'Jar': 'command-runner.jar',
                        'Args': base_args                    
                    }
                }
            ]
        )

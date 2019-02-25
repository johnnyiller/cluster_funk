from cluster_funk.core.clusters.emr_cluster \
    import EmrCluster


from mock import MagicMock

import pytest

client = MagicMock()
log = MagicMock()
cluster = EmrCluster(client, 'i-id1', log=log)


def test_init():
    assert cluster.log == log
    assert cluster.client == client
    assert cluster.cluster_id == 'i-id1'


def test_submit_job():

    cluster.client.add_job_flow_steps.return_value = 'success'

    resp = cluster.submit_spark_job('jobs/example1job',
                                    arguments=[
                                        '__JOB_PATH__/tests/fixtures/words.txt',
                                        's3://somedata/somewhere.csv'
                                    ])

    assert resp == 'success'
    cluster.client.add_job_flow_steps.assert_called_once_with(
        JobFlowId='i-id1',
        Steps=[
            {
                'Name': 'Spark cluster_funk',
                'ActionOnFailure': 'CONTINUE',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': [
                        'spark-submit',
                        '--deploy-mode',
                        'client',
                        'jobs/example1job/main.py',
                        'jobs/example1job/tests/fixtures/words.txt',
                        's3://somedata/somewhere.csv'
                    ]
                }
            }
        ]
    )

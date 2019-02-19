from cluster_funk.core.clusters.cluster_booter \
    import ClusterBooter

from mock import MagicMock, patch
import pytest


@pytest.fixture(scope='function')
def user_config():
    return {
        'Name': 'Test name',
        'Tags': {
            'Environment': 'dev',
            'Application': 'Sim'
        },
        'WorkLoadBucket': 'mybucketname',
        'WorkLoadPrefix': 'some/prefix/yesit/is',
        'Master': {
            'Instance': {
                'Count': 1,
                'Type': 't2.xlarge',
                'Storage': 50
            }
        },
        'Worker': {
            'Instance': {
                'Count': 4,
                'Type': 'c4.xlarge',
                'Storage': 100
            }
        },
        'PipInstall': [
            'pandas==3.4.2',
            'pytorch==1.20'
        ],
        'KeepJobFlowAliveWhenNoSteps': True
    }


def test_init(user_config, s3_client, emr_client):
    mock = MagicMock()

    def get_client(client_type, **kwargs):
        return {
            's3': s3_client,
            'emr': emr_client
        }.get(client_type)
    mock.client = get_client
    s3_client.create_bucket(Bucket='mybucketname')

    booter = ClusterBooter(user_config, mock)

    assert booter.emr_client == emr_client
    assert booter.s3_client == s3_client
    assert booter.bucket == 'mybucketname'
    assert booter.prefix == 'some/prefix/yesit/is'
    assert booter.user_config == user_config

    # a bunch of config asserts.
    c = booter.config
    assert c['LogUri'] == 's3n://mybucketname/some/prefix/yesit/is/logs'
    assert c['Name'] == 'Test name'

    master_group = c['Instances']['InstanceGroups'][0]
    assert master_group['InstanceRole'] == 'MASTER'
    assert master_group['InstanceCount'] == 1

    ebs = master_group['EbsConfiguration']['EbsBlockDeviceConfigs'][0]['VolumeSpecification']
    assert ebs['SizeInGB'] == 50

    slave_group = c['Instances']['InstanceGroups'][1]
    assert slave_group['InstanceRole'] == 'CORE'
    assert slave_group['InstanceCount'] == 4
    assert slave_group['InstanceType'] == 'c4.xlarge'

    ebs = slave_group['EbsConfiguration']['EbsBlockDeviceConfigs'][0]['VolumeSpecification']
    assert ebs['SizeInGB'] == 100
    expected = [
        {
            'Name': 'Install Python Libs',
            'ScriptBootstrapAction': {
                'Path': 's3://mybucketname/some/prefix/yesit/is/scripts/511dc9a47682bf930f8ece3e17f88592.sh'
            }
        }
    ]
    assert c['BootstrapActions'] == expected
    expected = set(['Spark', 'Livy', 'Hadoop', 'Hive'])
    actual = set([a['Name'] for a in c['Applications']])
    assert expected == actual

    expected = [
        {
            'Classification': 'emrfs-site',
            'Properties': {
                'fs.s3.consistent.retryPeriodSeconds': '10',
                'fs.s3.consistent': 'true',
                'fs.s3.consistent.retryCount': '5',
                'fs.s3.consistent.metadata.tableName': 'EmrFSMetadata'
            }
        },
        {
            'Classification': 'spark-defaults',
            'Properties': {
                'spark.yarn.appMasterEnv.SPARK_HOME': '/usr/lib/spark',
                'spark.yarn.appMasterEnv.PYSPARK_PYTHON': '/usr/bin/python3'
            }
        },
        {
            'Classification': 'yarn-site',
            'Properties': {
                'yarn.nodemanager.vmem-check-enabled': 'false'
            }
        },
        {
            'Classification': 'spark-env',
            'Configurations': [
                {
                    'Classification': 'export',
                    'Properties': {
                        'PYSPARK_PYTHON': '/usr/bin/python3'
                    }
                }
            ]
        },
        {
            'Classification': 'spark-hive-site',
            'Properties': {
                'hive.metastore.client.factory.class': 'com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory'
            }
        }
    ]
    assert expected == c['Configurations']

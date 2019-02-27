"""
PyTest Fixtures.
"""
import boto3

from moto import mock_emr, mock_s3, mock_cloudformation

import pytest
import contextlib
import os
import shutil
import tempfile
from mock import patch, MagicMock, create_autospec
from cement.ext.ext_logging import LoggingLogHandler


@contextlib.contextmanager
def cd(newdir, cleanup=lambda: True):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
        cleanup()


@contextlib.contextmanager
def tempdir():
    dirpath = tempfile.mkdtemp()

    def cleanup():
        shutil.rmtree(dirpath)

    with cd(dirpath, cleanup):
        yield dirpath


@pytest.fixture(scope="function")
def tmp(request):
    with tempdir() as dirpath:
        yield dirpath


@pytest.fixture(scope="function")
def job_collection_data(request):
    return [
        {
            'Id': 'j-djijsllkdk'
        },
        {
            'Id': 'j-djlkjldsjf'
        }
    ]


@pytest.fixture(scope="function")
def cluster_collection_data():
    return [
        {
            'Id': 'i-id1',
            'PublicDnsName': 'www.example.com',
            'PublicIpAddress': '192.156.22.221',
            'Status': {
                'State': 'RUNNING'
            }
        },
        {
            'Id': 'i-id2',
            'PublicDnsName': 'www.example2.com',
            'PublicIpAddress': '192.156.212.221',
            'Status': {
                'State': 'RUNNING'
            }
        }

    ]


@pytest.fixture(scope="function")
def stack_collection_data(request):
    return [
        {
            'Id': 's-id1',
            'Outputs': [
                {
                    'OutputKey': 'akey',
                    'OutputValue': 'avalue'
                }
            ]
        },
        {
            'Id': 's-id2',
            'Outputs': [
                {
                    'OutputKey': 'akeytwo',
                    'OutputValue': 'avaluetwo'
                }
            ]
        }
    ]


@pytest.fixture(scope='function')
def cloudformation_client(request):
    with mock_cloudformation():
        yield boto3.client('cloudformation', region_name='us-east-1')


@pytest.fixture(scope='function')
def s3_client(request):
    with mock_s3():
        yield boto3.client('s3', region_name='us-east-1')


@pytest.fixture(scope='function')
def emr_client(request):
    with mock_emr():
        yield boto3.client('emr', region_name='us-east-1')


@pytest.fixture(scope="function")
def emr_cluster(request):
    with mock_emr():
        emr_client = boto3.client('emr', region_name='us-east-1')
        emr_boot_cluster = {
            'Name': 'example_cluster',
            'LogUri': 's3://somes3bucket',
            'Instances': {
                'MasterInstanceType': 'c4.large',
                'SlaveInstanceType': 'c4.large',
                'InstanceCount': 3
            },
            'Tags': [
                {
                    'Key': 'user_id',
                    'Value': '123-456'
                }
            ]
        }
        cluster = emr_client.run_job_flow(**emr_boot_cluster)
        step_ids = emr_client.add_job_flow_steps(
            JobFlowId=cluster['JobFlowId'],
            Steps=[
                {
                    'Name': "example",
                    'ActionOnFailure': 'CONTINUE',
                    'HadoopJarStep': {
                        'Jar': 's3://runner.jar'
                    }
                },
                {
                    'Name': "example 2",
                    'ActionOnFailure': 'CONTINUE',
                    'HadoopJarStep': {
                        'Jar': 's3://runner.jar'
                    }
                }
            ]
        )
        yield (emr_client, cluster, step_ids)


@pytest.fixture(scope='function')
def ssh_connection(request):
    return MagicMock()


@pytest.fixture(scope='function')
def cluster_instance_params(request):
    return {
        'Id': 'c-testinstance',
        'PublicDnsName': 'my.dns.name',
        'PublicIpAddress': '234.543.22.123',
        'Status': {
            'State': 'RUNNING'
        }
    }


@pytest.fixture(scope='function')
def mock_uuid(request):
    mock = MagicMock(return_value='uuid-thing')
    with patch('uuid.uuid4', mock):
        yield {'mock': mock, 'uuid': 'uuid-thing'}


@pytest.fixture(scope='function')
def paginated_emr_client(emr_cluster):
    client = emr_cluster[0]
    m = MagicMock(return_value=client)
    page_mock = MagicMock()
    page_mock.paginate = MagicMock(return_value=[client.list_clusters()])
    m.get_paginator = page_mock
    with patch('cluster_funk.controllers.clusters.Clusters._emr_client', m):
        yield m


@pytest.fixture(scope='function')
def cluster_instance_mock():
    run_cmd_mock = MagicMock(return_value='run_cmd_called')
    syncfiles_mock = MagicMock(return_value='syncfiles_cmd_called')
    with patch('cluster_funk.core.clusters.cluster_instance.ClusterInstance.run_cmd', run_cmd_mock):
        with patch('cluster_funk.core.clusters.cluster_instance.ClusterInstance.syncfiles', syncfiles_mock):
            yield {
                'run_cmd': run_cmd_mock,
                'syncfiles': syncfiles_mock
            }


@pytest.fixture(scope='function')
def cluster_list_instances_mock(cluster_collection_data):
    mock = MagicMock()
    page_mock = MagicMock()
    page_mock.paginate.return_value = [{'Instances': cluster_collection_data}]
    mock.get_paginator.return_value = page_mock
    mock.describe_cluster.return_value = {'Cluster': {'MasterPublicDnsName': 'www.example.com'}}
    return MagicMock(return_value=mock)

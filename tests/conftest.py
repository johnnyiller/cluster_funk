"""
PyTest Fixtures.
"""
import boto3

from moto import mock_emr, mock_s3

import pytest
import contextlib
import os
import shutil
import tempfile
from mock import patch, MagicMock


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
            }
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
    m = MagicMock()
    return m


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

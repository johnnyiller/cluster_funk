from cluster_funk.core.clusters.cluster_instance \
    import ClusterInstance
from mock import MagicMock, patch, call
import pytest
import os
import re


@pytest.fixture(scope='function')
def instance(cluster_instance_params, ssh_connection):
    return ClusterInstance(
        cluster_instance_params,
        connect_kwargs={
            'some': 'arg'
        },
        connection_class=ssh_connection)


def test_from_instance(instance):
    assert instance.id == 'c-testinstance'
    assert instance.public_dns_name == 'my.dns.name'
    assert instance.state == 'RUNNING'
    assert instance.public_ip == '234.543.22.123'


def test_run_cmd(instance):
    instance.run_cmd('ls -hal')
    conn = instance.connection
    conn.run.assert_called_with('ls -hal')


def test_sudo_cmd(instance):
    instance.sudo_cmd('ls -hal')
    conn = instance.connection
    conn.sudo.assert_called_with('ls -hal')


def test_syncfiles_not_running(instance):
    instance.running = False
    with pytest.raises(BaseException) as notrunning:
        instance.syncfiles('adir', 'slslsdfkj/adir')
    assert 'That Cluster Instance isn\'t running' in str(notrunning)


def test_syncfiles_dir(instance, tmp, mock_uuid):
    os.mkdir('syncdir')
    os.mkdir(os.path.join('syncdir', '__pycache__'))
    f = open('syncdir/ex.txt', 'w')
    f.write('Example text')
    f.close()
    instance.syncfiles('syncdir', 'syncdirremote')
    conn = instance.connection

    called = conn.put.call_args_list[0]
    args, kwargs = called
    expr = re.compile("%s.tar.gz$" % mock_uuid['uuid'], re.IGNORECASE)

    assert bool(re.search(expr, args[0]))
    assert kwargs == {'remote': '/mnt/tmp'}

    run1, run2, run3 = conn.run.call_args_list
    assert run1[0][0] == 'tar -C /mnt/tmp -xzf /mnt/tmp/uuid-thing.tar.gz'
    assert run2[0][0] == 'rm -rf syncdirremote'
    assert run3[0][0] == 'mv /mnt/tmp/uuid-thing syncdirremote'


def test_syncfiles_file(instance):

    with patch('os.path.isdir', MagicMock(return_value=False)):
        with patch('os.path.isfile', MagicMock(return_value=True)):
            instance.syncfiles('tst.txt', '/home/hadoop/tstit.txt')

    instance.connection.put.assert_called_with('tst.txt', remote='/home/hadoop/tstit.txt')

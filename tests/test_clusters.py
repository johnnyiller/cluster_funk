from cluster_funk.main import ClusterFunkTest
from mock import patch, MagicMock, call

from cement.ext.ext_logging import LoggingLogHandler
import yaml


class Table:
    def all(self):
        return [{'id': '123-456'}]


def test_clusters_list(paginated_emr_client):
    argv = ['clusters', 'list', '-a']
    with ClusterFunkTest(argv=argv) as app:
        app.log.backend = MagicMock()
        app.run()
        output = app.log.backend.info.call_args_list[0][0][0]

    parsed = yaml.load(output)
    assert parsed['Status']['State'] == 'RUNNING'
    assert parsed['LogUri'] == 's3://somes3bucket'

    argv = ['clusters', 'list']
    with ClusterFunkTest(argv=argv) as app:
        app.log.backend = MagicMock()
        app.run()
        app.log.backend.assert_not_called()

    argv = ['clusters', 'list']
    with ClusterFunkTest(argv=argv) as app:
        app.log.backend = MagicMock()
        app.db = MagicMock()
        app.db.table.return_value = Table()
        app.run()
        app.db.table.assert_called_once_with('users')
        output = app.log.backend.info.call_args_list[0][0][0]

    parsed = yaml.load(output)
    assert parsed['Status']['State'] == 'RUNNING'
    assert parsed['LogUri'] == 's3://somes3bucket'


EXAMPLE_CONFIG = """
PipInstall:
    - "pandas==2.4"
    - "pyarrow>=1.2"
"""


def test_clusters_install(cluster_instance_mock, tmp, cluster_list_instances_mock):

    with open('exampleconf.yml', 'w') as f:
        f.write(EXAMPLE_CONFIG)

    log_mock = MagicMock()

    with patch('cluster_funk.controllers.clusters.Clusters._emr_client', cluster_list_instances_mock):
        argv = ['clusters', 'install', '-c', 'j-id1', '-f', 'exampleconf.yml', '-k', '~/.ssh/mykey.pem']
        with ClusterFunkTest(argv=argv) as app:
            app.log.backend = log_mock
            app.run()

    calls = [
        call('sudo /usr/bin/python3 -m pip install pandas==2.4 pyarrow>=1.2'),
        call('sudo /usr/bin/python3 -m pip install pandas==2.4 pyarrow>=1.2')
    ]
    cluster_instance_mock['run_cmd'].assert_has_calls(calls)

    msgs = [msg[0][0] for msg in app.log.backend.info.call_args_list]
    expected_messages = [
        '\nInstalling dependencies on www.example.com',
        'run_cmd_called',
        '\nInstalling dependencies on www.example2.com',
        'run_cmd_called'
    ]
    assert msgs == expected_messages


def test_clusters_run_cmd(cluster_instance_mock, cluster_list_instances_mock):
    log_mock = MagicMock()
    with patch('cluster_funk.controllers.clusters.Clusters._emr_client', cluster_list_instances_mock):
        argv = ['clusters', 'run-cmd', '-c', 'j-id1', '-k', '~/.ssh/mykey.pem', '-r', 'ls -hal']
        with ClusterFunkTest(argv=argv) as app:
            app.log.backend = log_mock
            app.run()
            msgs = [msg[0][0] for msg in app.log.backend.info.call_args_list]

    expected_calls = [call('ls -hal') for i in range(2)]
    cluster_instance_mock['run_cmd'].has_calls(expected_calls)

    expected_messages = [
        '\nRunning command on host www.example.com',
        'run_cmd_called',
        '\nRunning command on host www.example2.com',
        'run_cmd_called'
    ]
    assert msgs == expected_messages

    log_mock.reset_mock()
    cluster_instance_mock['run_cmd'].reset_mock()

    # call with master only flag set
    with patch('cluster_funk.controllers.clusters.Clusters._emr_client', cluster_list_instances_mock):
        argv = ['clusters', 'run-cmd', '-c', 'j-id1', '-k', '~/.ssh/mykey.pem', '-r', 'ls -hal', '-m']
        with ClusterFunkTest(argv=argv) as app:
            app.log.backend = log_mock
            app.run()
            msgs = [msg[0][0] for msg in app.log.backend.info.call_args_list]

    cluster_instance_mock['run_cmd'].assert_called_once_with('ls -hal')
    expected_messages = [
        '\nRunning command on host www.example.com',
        'run_cmd_called'
    ]
    assert expected_messages == msgs

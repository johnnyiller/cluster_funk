from cluster_funk.main import ClusterFunkTest
from mock import patch, MagicMock

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

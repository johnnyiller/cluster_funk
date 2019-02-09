from unittest.mock import patch

from cluster_funk.main import ClusterFunkTest


@patch('cluster_funk.main.ClusterFunkTestLoggingLogHandler.info')
def test_jobs_list(infoMock):

    def mock_init(self, *args, **kwargs):
        self.list = []

    with patch(
        'cluster_funk.core.jobs.job_collection.JobCollection.__init__',
        new=mock_init
    ):

        argv = ['jobs', 'list', '-c', 'j-fakeid']
        with ClusterFunkTest(argv=argv) as app:
            app.run()

    expected = "We didn't find any jobs for that cluster.  please check the cluster id"  # noqa
    infoMock.assert_called_with(expected)

    def mock_init(self, *args, **kwargs):
        self.list = [{'Id': 's-nonsensestuff'}]

    with patch(
        'cluster_funk.core.jobs.job_collection.JobCollection.__init__',
        new=mock_init
    ):

        argv = ['jobs', 'list', '-c', 'j-fakeid']
        with ClusterFunkTest(argv=argv) as app:
            app.run()

    expected = '\n----------------------------\n{Id: s-nonsensestuff}\n'
    infoMock.assert_called_with(expected)


def test_jobs_submit():
    pass

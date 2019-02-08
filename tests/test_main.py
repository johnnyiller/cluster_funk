
from cluster_funk.main import ClusterFunkTest


def test_cluster_funk(tmp):
    with ClusterFunkTest() as app:
        res = app.run()
        print(res)


def test_clusters(tmp):
    argv = ['clusters']
    with ClusterFunkTest(argv=argv) as app:
        app.run()


def test_jobs(tmp):
    argv = ['jobs']
    with ClusterFunkTest(argv=argv) as app:
        app.run()

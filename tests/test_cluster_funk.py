import os

from pytest import raises
from cluster_funk.main import ClusterFunkTest


def test_cluster_funk():
    # test cluster_funk without any subcommands or arguments
    with ClusterFunkTest() as app:
        app.run()
        assert app.exit_code == 0


def test_cluster_funk_debug():
    # test that debug mode is functional
    argv = ['--debug']
    with ClusterFunkTest(argv=argv) as app:
        app.run()
        assert app.debug is True


def test_cluster_funk_new(tmp):
    # Test that our directory structure with base files gets created...
    argv = ['new', 'example_app']
    with ClusterFunkTest(argv=argv) as app:
        app.run()

    new_path = os.path.join(tmp, 'example_app')
    environment_path = os.path.join(new_path, "environments")
    environment_paths = [
        os.path.join(environment_path, p) for p in ['dev', 'prd', 'stg']
    ]

    for directory, subdirectory, files in os.walk(new_path):

        if directory == new_path:
            assert set(['.cf', 'environments', 'jobs']) == set(subdirectory)
            assert ['README.md'] == files

        if directory == environment_path:
            assert set(['prd', 'dev', 'stg']) == set(subdirectory)

        if directory in environment_paths:
            assert set(['vpc.yml', 'iam.yml']) == set(files)

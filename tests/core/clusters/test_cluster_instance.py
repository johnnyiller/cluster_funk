from cluster_funk.core.clusters.cluster_instance \
    import ClusterInstance
from mock import MagicMock, patch


def test_from_instance(cluster_instance_params, ssh_connection):

    instance = ClusterInstance(
        cluster_instance_params,
        connect_kwargs={
            'some': 'arg'
        },
        connection_class=ssh_connection)

    assert instance.id == 'c-testinstance'

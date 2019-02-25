from cluster_funk.core.clusters.cluster_instance_collection \
    import ClusterInstanceCollection
from cluster_funk.core.clusters.cluster_instance \
    import ClusterInstance

from mock import patch, MagicMock, call


def test_with_data(cluster_collection_data):
    collection = ClusterInstanceCollection(data=cluster_collection_data)
    assert len(collection) == len(cluster_collection_data)
    assert collection[0]['Id'] == cluster_collection_data[0]['Id']
    assert str(collection) == str(cluster_collection_data)
    reversed_it = collection.reverse()
    assert len(reversed_it)
    assert reversed_it != collection
    current_length = len(collection)
    del collection[0]
    assert len(collection) == current_length - 1
    collection.insert(0, {'Id': 'nonsense'})
    assert collection[0] == {'Id': 'nonsense'}
    assert len(collection) == current_length

    def filter_expr(item):
        return item['Id'] == 'i-id2'

    output = collection.filter_by(filter_expr)
    assert collection != output
    assert output[0]['Id'] == 'i-id2'
    assert len(output) == 1
    tst_data = {'Id': 'nonensesetst'}
    collection[0] = tst_data
    assert collection[0] == tst_data


def test_without_data(cluster_collection_data):
    mock = MagicMock()
    page_mock = MagicMock()
    page_mock.paginate.return_value = [{'Instances': cluster_collection_data}]
    mock.get_paginator.return_value = page_mock

    collection = ClusterInstanceCollection(
        cluster_key='~/.ssh/mykey',
        client=mock
    )

    assert isinstance(collection[0], ClusterInstance)
    mock.get_paginator.assert_called_with('list_instances')


def test_syncfiles():

    log_mock = MagicMock()

    def ci_mock(i):
        m = MagicMock()
        m.public_dns_name = "happy.domain%s.com" % i
        m.syncfiles.return_value = "copies"
        return m

    data = [ci_mock(i) for i in range(2)]
    collection = ClusterInstanceCollection(data=data, log=log_mock)
    collection.syncfiles("asource", "adest")
    calls = [
        call.info('\n\nCopy file or folder asource, to happy.domain0.com:adest'),
        call.info("Copied files:\n copies"),
        call.info('\n\nCopy file or folder asource, to happy.domain1.com:adest'),
        call.info("Copied files:\n copies")
    ]

    assert log_mock.mock_calls == calls
    data[0].syncfiles.assert_called_once_with("asource", "adest")
    data[1].syncfiles.assert_called_once_with("asource", "adest")

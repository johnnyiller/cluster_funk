from cluster_funk.core.environments.stack_collection \
    import StackCollection

from mock import MagicMock


def test_with_data(stack_collection_data):
    # tests initializing the object and filtering and filtering the collection
    collection = StackCollection(data=stack_collection_data)
    outputs = collection.output_dict()
    assert outputs['akey'] == 'avalue'
    assert outputs['akeytwo'] == 'avaluetwo'
    assert len(collection) == len(stack_collection_data)
    assert collection[0]['Id'] == stack_collection_data[0]['Id']
    assert str(collection) == str(stack_collection_data)
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
        return item['Id'] == 's-id2'

    output = collection.filter_by(filter_expr)
    assert collection != output
    assert output[0]['Id'] == 's-id2'
    assert len(output) == 1
    tst_data = {'Id': 'nonensesetst'}
    collection[0] = tst_data
    assert collection[0] == tst_data


def test_without_data(stack_collection_data):
    mock = MagicMock()
    pagemock = MagicMock()
    pagemock.paginate.return_value = [{'Stacks': stack_collection_data}]
    mock.get_paginator.return_value = pagemock

    collection = StackCollection(client=mock)
    stackids = [stack['Id'] for stack in collection]

    mock.get_paginator.assert_called_once_with('describe_stacks')
    pagemock.paginate.assert_called_once()
    assert stackids == ['s-id1', 's-id2']


def test_has_prefix():
    stack = {
        'Tags': [
            {
                'Key': 'Name',
                'Value': 'prefixer-is-great'
            }
        ]
    }
    assert StackCollection.has_prefix('prefixer', stack)
    assert StackCollection.has_prefix('notprefixer', stack) == False


def test_is_cf_stack():
    stack = {
        'Tags': [
            {
                'Key': 'tool',
                'Value': 'cluster_funk'
            }
        ]
    }
    assert StackCollection.is_cf_stack(stack)
    stack['Tags'][0]['Value'] = "not_cluster_funk"
    assert StackCollection.is_cf_stack(stack) == False


def test_has_env():
    stack = {
        'Tags': [
            {
                'Key': 'environment',
                'Value': 'prd'
            }
        ]
    }
    assert StackCollection.has_env("prd", stack)
    assert StackCollection.has_env("noprod", stack) == False

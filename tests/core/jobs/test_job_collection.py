from cluster_funk.core.jobs.job_collection import JobCollection


def test_with_data(job_collection_data):
    # tests initializing the object and filtering and filtering the collection
    collection = JobCollection(data=job_collection_data)
    assert len(collection) == len(job_collection_data)
    assert collection[0]['Id'] == job_collection_data[0]['Id']
    assert str(collection) == str(job_collection_data)
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
        return item['Id'] == 'j-djlkjldsjf'

    output = collection.filter_by(filter_expr)
    assert collection != output
    assert output[0]['Id'] == 'j-djlkjldsjf'
    assert len(output) == 1
    tst_data = {'Id': 'nonensesetst'}
    collection[0] = tst_data
    assert collection[0] == tst_data


def test_job_collection_without_job_id(emr_cluster):
    client, cluster, steps = emr_cluster
    collection = JobCollection(
        client=client,
        cluster_id=cluster['JobFlowId'],
        states=['STARTING', 'COMPLETED']
    )
    assert len(collection) != 0
    assert collection[0]['Id'].startswith("s-")


def test_job_collection_with_job_id(emr_cluster):
    client, cluster, step_ids = emr_cluster
    collection = JobCollection(
        client=client,
        cluster_id=cluster['JobFlowId'],
        job_id=step_ids['StepIds'][0]
    )
    assert len(collection) == 1
    assert collection[0]['Id'].startswith("s-")

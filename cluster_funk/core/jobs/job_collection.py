class JobCollection:

    def __init__(
            self, client=None, cluster_id=None,
            job_id=None, states=None, data=None):

        super()

        if data is None:
            self.list = list()
            if job_id:
                step = client.describe_step(
                    ClusterId=cluster_id,
                    StepId=job_id
                )
                self.list.append(step['Step'])
            else:
                pager_args = {
                    'ClusterId': cluster_id
                }

                if states:
                    pager_args['StepStates'] = states

                paginator = client.get_paginator('list_steps')
                results = paginator.paginate(**pager_args)
                for result in results:
                    for step in result['Steps']:
                        self.list.append(step)
        else:
            self.list = list(data)

    def __len__(self):
        return len(self.list)

    def __getitem__(self, ii):
        return self.list[ii]

    def __delitem__(self, ii):
        del self.list[ii]

    def __setitem__(self, ii, val):
        self.list[ii] = val

    def __str__(self):
        return str(self.list)

    def reverse(self):
        return self[::-1]

    def insert(self, ii, val):
        self.list.insert(ii, val)

    def filter_by(self, func):
        filtered = [job for job in self.list if func(job)]
        return JobCollection(data=filtered)

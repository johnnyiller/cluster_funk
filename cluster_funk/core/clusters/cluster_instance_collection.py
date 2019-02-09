import logging

from .cluster_instance import ClusterInstance


class ClusterInstanceCollection:

    def __init__(self, client=None, cluster_id=None,
                 states=None, data=None, cluster_key=None, log=logging.Logger("cluster_funk")):
        self.log = log
        super()
        if data is None:
            self.list = []
            paginator = client.get_paginator('list_instances')
            response_iterator = paginator.paginate(ClusterId=cluster_id)

            for response in response_iterator:
                for instance in response['Instances']:
                    self.list.append(ClusterInstance(
                        instance, {"key_filename": [cluster_key]}))
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
        filtered = [instance for instance in self.list if func(instance)]
        return ClusterInstanceCollection(data=filtered)

    def syncfiles(self, src, dest):
        for ci in self.list:
            self.log.info("\n\nCopy file or folder %s, to %s:%s" %
                          (src, ci.public_dns_name, dest))
            result = ci.syncfiles(src, dest)
            self.log.info("Copied files:\n %s" % result)
        return self

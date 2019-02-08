class StackCollection:

    def __init__(self, client=None, data=None):
        super(StackCollection, self).__init__()
        if data==None:
            paginator = client.get_paginator('describe_stacks')
            results = paginator.paginate()
            self.list = list()
            for result in results:
                stacks = result['Stacks']
                for stack in stacks:
                    self.list.append(stack)
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
    
    def insert(self, ii, val):
        self.list.insert(ii, val)

    def filter_by(self, func):
        filtered = [stack for stack in self.list if func(stack)]
        return StackCollection(data=filtered)
    
    @staticmethod
    def has_prefix(stack_prefix, stack):
        for tag in stack.get('Tags', []):
            if tag['Key'] == 'Name' and tag.get('Value',"").startswith(stack_prefix):
                return True
        return False
    
    @staticmethod
    def is_cf_stack(stack):
        for tag in stack.get('Tags', []):
            if tag['Key'] == 'tool' and tag['Value'] == 'cluster_funk':
                return True
        return False
    
    @staticmethod
    def has_env(env, stack):
        for tag in stack.get('Tags', []):
            if tag['Key'] == 'environment' and tag['Value'] == env:
                return True
        return False

    def output_dict(self):
        result = {}
        
        for stack in self:
            for output in stack.get("Outputs", []):
                result[output.get("OutputKey", "")] = output["OutputValue"]

        return result

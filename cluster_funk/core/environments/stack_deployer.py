import boto3


class StackDeployer:

    def __init__(self, user_id, profile, stack_prefix, env, stack_type, capabilities=['CAPABILITY_NAMED_IAM']):
        self.profile = profile
        self.capabilities = capabilities
        self.stack_prefix = stack_prefix
        self.env = env
        self.stack_type = stack_type
        self.user_id = user_id
        self.stack_name = "{stack_prefix}-{env}-{stack_type}".format(
            stack_prefix=stack_prefix, env=env, stack_type=stack_type)
        self.template_body = open(
            "./environments/{env}/{stack_type}.yml".format(env=env, stack_type=stack_type), 'r').read()

    def deploy(self):
        session = boto3.session.Session(profile_name=self.profile)
        client = session.client('cloudformation')
        try:
            response = client.create_stack(
                StackName=self.stack_name,
                TemplateBody=self.template_body,
                Capabilities=self.capabilities,
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': self.stack_name
                    },
                    {
                        'Key': 'Application',
                        'Value': 'Emr Spark'
                    },
                    {
                        'Key': 'Tier',
                        'Value': 'APP'
                    },
                    {
                        'Key': 'Environment',
                        'Value': self.env.upper()
                    },
                    {
                        'Key': 'TechnicalTeam',
                        'Value': 'Architecture'
                    },
                    {
                        'Key': 'tool',
                        'Value': 'cluster_funk'
                    },
                    {
                        'Key': 'type',
                        'Value': self.stack_type
                    },
                    {
                        'Key': 'user_id',
                        'Value': self.user_id
                    },
                    {
                        'Key': 'environment',
                        'Value': self.env
                    }
                ],
                OnFailure='ROLLBACK',
                EnableTerminationProtection=True
            )
            waiter = client.get_waiter('stack_create_complete')

            def wait_func():
                waiter.wait(
                    StackName=response['StackId'],
                    WaiterConfig={
                        'Delay': 30,
                        'MaxAttempts': 60
                    }
                )
            return (wait_func, response)
        except client.exceptions.AlreadyExistsException:
            try:
                response = client.update_stack(
                    StackName=self.stack_name,
                    TemplateBody=self.template_body,
                    Capabilities=self.capabilities
                )
                waiter = client.get_waiter('stack_update_complete')

                def wait_func():
                    waiter.wait(
                        StackName=response['StackId'],
                        WaiterConfig={
                            'Delay': 30,
                            'MaxAttempts': 60
                        }
                    )
                return (wait_func, response)
            except client.exceptions.ClientError as nochanges:
                return (None, {'message': str("%s -> %s" % ("no changes to apply", nochanges))})

        return (None, {'message': 'no operation performed'})

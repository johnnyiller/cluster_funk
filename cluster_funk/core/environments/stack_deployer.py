import boto3


class StackDeployer:

    def __init__(self, user_id, profile, stack_prefix, env,
                 stack_type, capabilities=['CAPABILITY_NAMED_IAM']):
        self.profile = profile
        self.capabilities = capabilities
        self.stack_prefix = stack_prefix
        self.env = env
        self.stack_type = stack_type
        self.user_id = user_id
        self.stack_name = "{stack_prefix}-{env}-{stack_type}".format(
            stack_prefix=stack_prefix, env=env, stack_type=stack_type)
        self.body_path = "./environments/{env}/{stack_type}.yml".format(
            env=env,
            stack_type=stack_type)

    def _session(self):
        return boto3.session.Session(profile_name=self.profile)

    def _cloudformation_client(self):
        return self._session().client('cloudformation')

    def _get_template_body(self):
        return open(self.body_path, 'r').read()

    def create_stack(self, client):
        template_body = self._get_template_body()
        response = client.create_stack(
            StackName=self.stack_name,
            TemplateBody=template_body,
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

        def wait_func(waiter=client.get_waiter('stack_create_complete')):
            waiter.wait(
                StackName=response['StackId'],
                WaiterConfig={
                    'Delay': 30,
                    'MaxAttempts': 60
                }
            )
        return (wait_func, response)

    def update_stack(self, client):

        template_body = self._get_template_body()
        response = client.update_stack(
            StackName=self.stack_name,
            TemplateBody=template_body,
            Capabilities=self.capabilities
        )

        def wait_func(waiter=client.get_waiter('stack_update_complete')):
            waiter.wait(
                StackName=response['StackId'],
                WaiterConfig={
                    'Delay': 30,
                    'MaxAttempts': 60
                }
            )
        return (wait_func, response)

    def deploy(self, create_stack_exception=None, update_stack_exception=None):
        client = self._cloudformation_client()

        create_stack_exception = create_stack_exception or client.exceptions.AlreadyExistsException
        update_stack_exception = update_stack_exception or client.exceptions.ClientError

        try:
            return self.create_stack(client)
        except create_stack_exception:
            try:
                return self.update_stack(client)
            except update_stack_exception as nochanges:
                return (None, {'message': str("%s -> %s" % ("no changes to apply", nochanges))})

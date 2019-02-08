import boto3
import os
import re
import yaml
from functools import partial

from cement import Controller, ex
from ..core.environments.stack_deployer import StackDeployer
from ..core.environments.stack_collection import StackCollection
from ..core.utils import environment_names, template_names

class Environments(Controller):

    class Meta:
        label = 'environments'
        stacked_type = 'nested'
        stacked_on = 'base'
        help = 'Deploy and inspect your environment (security settings)'
    
    @ex(
        help='deploy environment',
        arguments=[
            (['-e', '--env'], { 
                'help': 'Environment name (default: dev)', 
                'action': 'store',
                'choices': environment_names(),
                'default': 'dev'
            }),
            (['-s', '--stack-prefix'], { 
                'help': 'The cloudforamtion stack prefix (default: emr-spark)', 
                'action': 'store',
                'default': 'emr-spark'
            }),
            (['-p', '--profile'], {
                'help': 'AWS profile (default: default)',
                'action': 'store',
                'default': 'default'
            })
        ]
    )
    def deploy(self):
        cliargs = self.app.pargs
        stack_prefix = cliargs.stack_prefix
        env = cliargs.env

        try:
            table = self.app.db.table('users')
            user_id = table.all()[0]['id']
        except IndexError:
            user_id = None

        if not user_id:
            self.app.log.error("You must set your user_id in order to create a stack, for tagging :)")
            return None

        for stack_type in template_names(env):
            self.app.log.info("%s - Update Starting" % stack_type)

            deployer = StackDeployer(
                user_id=user_id, 
                profile=cliargs.profile, 
                stack_prefix=stack_prefix, 
                env=env, 
                stack_type=stack_type)

            wait, resp = deployer.deploy()

            if wait:
                self.app.log.info("Updating %s This can take a couple minutes please sit tight." % (stack_type))
                wait()

            self.app.log.info("%s - Update Complete" % stack_type)
            self.app.log.info(resp)

    @ex(
        help='Get outputs from cloudformation',
        arguments=[
            (['-e', '--env'], { 
                'help': 'Environment name (default: dev)', 
                'action': 'store',
                'choices': environment_names(),
                'default': 'dev'
            }),
            (['-p', '--profile'], {
                'help': 'AWS profile (default: default)',
                'action': 'store',
                'default': 'default'
            })
        ]
    )
    def outputs(self):
        profile_name = self.app.pargs.profile
        env = self.app.pargs.env
        for stack in self._get_cf_details(profile_name, env):
            self.app.log.info("Stack Id: {id}".format(id=stack['StackId']))
            print(yaml.dump(stack['Outputs']))

    
    @ex(
        help='Get full details from cloudformation',
        arguments=[
            (['-e', '--env'], { 
                'help': 'Environment name (default: dev)', 
                'action': 'store',
                'choices': environment_names(),
                'default': 'dev'
            }),
            (['-p', '--profile'], {
                'help': 'AWS profile (default: default)',
                'action': 'store',
                'default': 'default'
            })
        ]
    )
    def details(self):
        profile_name = self.app.pargs.profile
        env = self.app.pargs.env
        for stack in self._get_cf_details(profile_name, env):
            self.app.log.info("Stack Id: {id}".format(id=stack['StackId']))
            print(yaml.dump(stack))


    def _get_cf_details(self, profile_name, env):
        session = boto3.session.Session(profile_name=profile_name)
        client = session.client('cloudformation')
        stacks = StackCollection(client)
        stacks = stacks.filter_by(StackCollection.is_cf_stack)
        return stacks.filter_by(partial(StackCollection.has_env, env))


import re
import argparse


def cluster_id(overwrite={}):
    opts = {
        'help': 'Cluster id that the job ran on',
        'required': True
    }
    return (['-c', '--cluster-id'], {**opts, **overwrite})


def profile(overwrite={}):
    opts = {
        'help': 'AWS profile',
        'default': 'default'
    }
    return (['-p', '--profile'], {**opts, **overwrite})


def job_id(overwrite={}):
    opts = {
        'help': 'filter results by a specific job id'
    }
    return (['-j', '--job-id'], {**opts, **overwrite})


def job_state(overwrite={}):
    opts = {
        'help': 'Filter by state.  Can be used multiple times',
        'choices': ['PENDING', 'CANCEL_PENDING', 'RUNNING', 'COMPLETED', 'CANCELLED', 'FAILED', 'INTERRUPTED'],
        'action': 'append'
    }
    return (['-s', '--state'], {**opts, **overwrite})


def job_name(overwrite={}):

    def name_type(string):
        if not re.match(r'^\w+$', string):
            raise argparse.ArgumentTypeError
        return string

    opts = {
        'help': 'The name of the job valid format [A-Z][a-z][0-9]_',
        'action': 'store',
        'required': True,
        'type': name_type
    }

    return (['-n', '--name'], {**opts, **overwrite})


def job_on_failure(overwrite={}):
    opts = {
        'help': 'Action on failure of the job',
        'choices': ['TERMINATE_JOB_FLOW', 'TERMINATE_CLUSTER', 'CANCEL_AND_WAIT', 'CONTINUE'],
        'default': 'CONTINUE'
    }
    return (['-f', '--on-failure'], {**opts, **overwrite})


def job_on_success(overwrite={}):
    opts = {
        'help': 'Action on step success',
        'choices': ['TERMINATE_CLUSTER', 'CONTINUE'],
        'default': 'CONTINUE'
    }
    return (['-s', '--on-success'], {**opts, **overwrite})


def job_argument(overwrite={}):
    opts = {
        'help': 'Optional arguments to pass to your main.py use more than once for many args',
        'action': 'append',
        'type': str
    }
    return (['-a', '--argument'], {**opts, **overwrite})


def ssh_key_location(overwrite={}):
    opts = {
        'help': 'location of ssh key to log into cluster nodes',
        'required': True
    }
    return (['-k', '--ssh-key'], {**opts, **overwrite})

[![Build Status](https://travis-ci.org/johnnyiller/cluster_funk.svg?branch=master)](https://travis-ci.org/johnnyiller/cluster_funk)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=bugs)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=code_smells)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=coverage)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=security_rating)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=johnnyiller_cluster_funk&metric=sqale_index)](https://sonarcloud.io/dashboard?id=johnnyiller_cluster_funk)



# Requirements
1. python >= 3.6 
1. Some variant of linux.  Use docker on windows?

# Installation

1. Update your pip version.
    ```bash
    python -m pip install --upgrade pip
    ```
1. Make sure you have an AWS account with permission to create EMR resources and ec2-keys.

1. Install the cluster_funk cli to get started.
    ```bash
    pip install cluster_funk
    ```
1. [Install and configure the aws-cli if you haven't already](https://aws.amazon.com/cli/)
    ```
    pip install awscli
    aws configure
    ```

# Getting Started

Probably the most important thing to know about the CLI is that you can get help on any command directly from the command line by appending -h or --help to any command and reading the output. 

For example, to get help on base level commands you can type.

```bash
cluster_funk -h
```

## A new project (Infrequently done)

Generally, you will rarely create a new project.  Far more common will be creating a new job.  However, it is still worth going over the process to add clarity to this CLI.

This project makes extensive use of S3 for logging and code storage.  Additionally, you'll likely want an s3 bucket for data storage. Thus, you must either create a new S3 bucket or use an existing one.

### Create an S3 Bucket

This would create a bucket called mybucket.  You'll want to name your bucket something more descriptive.

```bash
aws s3 mb s3://mybucket
```

### Create the application skeleton.  

This will lay out the basic directory structure for your jobs and copy over some cloudformation templates used to provision environments.

```bash
cluster_funk new my_new_project
```
This will create a directory named my_new_project which will have two top level directories.  Click links for more detail about what type of code / configuration resides in each of these directories.

- [/environments](./environments)
- [/jobs](./jobs)

### Deploy an environment

Your AWS CLI must be configured properly for this to work.  By default we will use your default AWS profile. You can pass in the -p option if you want to use a different account.

```bash
cluster_funk environments deploy
```

This will deploy the environment with the dev environment set.  All commands support the -h option if you'd like to understand what other options are available for this command. 

Verify the environment is set up by either logging into the AWS console and inspecting your cloudformation stacks or you can type.

```bash
cluster_funk environments details -e dev
```

If everything deployed without incident you should be able to start developing jobs.

## Working on an existing project

### Generate source code for an example job

Once you have a project and an environment created you'll want to make your first job.  Generally speaking a job consists of the code that needs to execute as well as the config file for the cluster for each environment.  Cluster configuration might be very different between environments.  Thus, a separate cluster config file is created for each environment.  To generate a source code skeleton for a job type.

```bash
cluster_funk jobs generate -n UNIQUE_NAME_FOR_JOB
```

### Generate a cluster config for your environment

```bash
cluster_funk clusters generate-config -e dev -b SOMES3BUCKET -j example_job
```
<em>If you did not use the environment config files provided by this framework you may need to make significant changes to the generated cluster config file.</em>

Check the config file and change any settings you think need adjusting.  For example if you expect to use some specific pip libraries you should add them to the PipInstall property.

### Boot the cluster

```bash
cluster_funk clusters boot -k myec2-key -c ./PATH/TO/config.yml -Y
```

Check the status of your clusters:

```bash
cluster_funk clusters list
```

You can also log into the EMR console and browse the console.  We recommend you familiarize yourself with the EMR console and all that it offers in the way of monitoring and web based UI's.

### Submit a job

Once your cluster is booted up you can start submitting your jobs to the cluster as part of your development workflow.

To submit a job type to following.

```bash
cluster_funk jobs submit -k /SSH/KEY/PATH/keyname -a __JOB_PATH__/tests/fixtures/words.txt -n job_name -c cluster_id
```

By convention the job runner will run the main.py file with arguments specified by -a.  You will likely want to use arguments to parameterize your config data such that a job can move between environments without being re-written.

### Extra Credit

Lastly, you may want to connect a sagemaker notebook and connect it to the cluster (tooling coming soon...)

### Notes

This project is very early stage is not yet recommended for production use.  Use at your own risk.

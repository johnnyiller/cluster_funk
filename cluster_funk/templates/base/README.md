# Cluster-Funk
## Apache Spark Jobs Running on Amazon EMR

The organization of jobs is pretty simple and aims to be self contained. Each job reside in it's own
subdirectory.  Within each sub-directory are files that are used to configure the cluster the job runs
on as well as define the dependencies and code required to run the job.

Directories are as follows:
1. jobs (top level directory for EMR jobs)
2. environments (collection of cloudformation templates used to build VPC, IAM, and Security Groups)

After installing the cluster_funk tool you can create a new job by typing
```
cluster_funk jobs create --name my_new_job_name
```

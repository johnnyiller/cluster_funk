# Environments

Environments lay out the infrastructure that is required in order to run your jobs.  At a basic level this means you need a VPC and well defined IAM security roles. VPC's set up the networking requirements and IAM set's up the Role based authentication EMR needs to boot a cluster.

Additionally you can add other requirements to the environment in this directory structure.  For example if your jobs require a dynamodb table or permission to some other AWS account you might specify those requirements in the environments directory.  

If you have access to a devops or architect resource at your company you may want to consult them before making sweeping changes to the environment.

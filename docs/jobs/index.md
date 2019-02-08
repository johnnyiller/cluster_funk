# Jobs

Jobs is the core component in a cluster_funk project.  Most developers will spend the majority of their time programming their specifc job to analyze data.  

*At this time cluster_funk does not support streaming or always on jobs.  All clusters are transient and should be treated as if they can be destroyed.

In short HDFS might be used to run a specific job but will not persist between job runs.  Please take this into account when running your job.*

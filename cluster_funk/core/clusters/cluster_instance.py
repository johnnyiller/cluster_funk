import os
import uuid
import tarfile

from fabric.connection import Connection
from cement.utils import fs

class ClusterInstance:

    # pass the connection class in just in case we want to send in a mock
    def __init__(self, instance_params, connect_kwargs={}):
        self.intance_params = instance_params
        self.id = instance_params['Id']
        self.public_dns_name = instance_params['PublicDnsName']
        self.public_ip = instance_params['PublicIpAddress']
        self.state = instance_params['Status']['State']
        self.running = False

        if self.state == 'RUNNING':
            self.running = True

        self.connection = Connection(
            host=self.public_dns_name,
            user='hadoop',
            port=22,
            connect_kwargs=connect_kwargs
        )

    def run_cmd(self, cmd):
        return self.connection.run(cmd)

    def sudo_cmd(self, cmd):
        return self.connection.sudo(cmd)
    
    def syncfiles(self, src, dest):

        if not self.running:
            raise "That Cluster Instance isn't running, can't copy files"

        if os.path.isdir(src):

            EXCLUDE_FILES = ['__pycache__', '.git', '.gitignore']

            def filter_function(tarinfo):
                for filename in EXCLUDE_FILES:
                    if filename in tarinfo.name:
                        return None
                return tarinfo

            with fs.Tmp() as tmp:

                filename = uuid.uuid4()
                temp_file = "%s/%s.tar.gz" % (tmp.dir, filename)

                with tarfile.open(temp_file, "w:gz") as tar:
                    tar.add(src, recursive=True, arcname=str(filename), filter=filter_function)

                self.connection.put(temp_file, remote='/mnt/tmp') 
                self.run_cmd("tar -C /mnt/tmp -xzf /mnt/tmp/%s.tar.gz" % (filename))
                self.run_cmd("rm -rf %s" % (dest))
                return self.run_cmd("mv /mnt/tmp/%s %s" % (filename, dest))

        if os.path.isfile(src):
            return self.connection.put(src, remote=dest) 

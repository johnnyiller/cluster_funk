import json

class SagemakerNotebookBooter:
    pass
"""
    def __init__(self, cluster_id, session):
        self.cluster_id = cluster_id
        self.emr_client = session.client('emr') 
        self.details = None
        self.set_cluster_details()

    def set_cluster_details(self):
        if self.details:
            return self.details
        else:
            self.details = self.emr_client.describe_cluster(ClusterId=self.cluster_id)
            return self.details


    def _spark_magic_config(self, livy_url="http://localhost:8998"):
        return {
            "kernel_python_credentials": {
                "username": "",
                "password": "",
                "url": livy_url,
                "auth": "None"
            },
            "kernel_scala_credentials": {
                "username": "",
                "password": "",
                "url": livy_url,
                "auth": "None"
            },
            "kernel_r_credentials": {
                "username": "",
                "password": "",
                "url": livy_url
            },
            "logging_config": {
                "version": 1,
                "formatters": {
                    "magicsFormatter": {
                        "format": "%(asctime)s\t%(levelname)s\t%(message)s",
                        "datefmt": ""
                    }
                },
                "handlers": {
                    "magicsHandler": { 
                        "class": "hdijupyterutils.filehandler.MagicsFileHandler",
                        "formatter": "magicsFormatter",
                        "home_path": "~/.sparkmagic"
                    }
                },
                "loggers": {
                    "magicsLogger": {
                        "handlers": ["magicsHandler"],
                        "level": "DEBUG",
                        "propagate": 0
                    }
                }
            },
            "wait_for_idle_timeout_seconds": 30,
            "livy_session_startup_timeout_seconds": 120,
            "fatal_error_suggestion": "The code failed because of a fatal error:\n\t{}.\n\nSome things to try:\na) Make sure Spark has enough available resources for Jupyter to create a Spark context.\nb) Contact your Jupyter administrator to make sure the Spark magics library is configured correctly.\nc) Restart the kernel.",    
            "ignore_ssl_errors": False,
            "session_configs": {
                "driverMemory": "8000M",
                "executorCores": 4
            },
            "use_auto_viz": True,
            "coerce_dataframe": True,
            "max_results_sql": 2500,
            "pyspark_dataframe_encoding": "utf-8",
            "heartbeat_refresh_seconds": 30,
            "livy_server_heartbeat_timeout_seconds": 0,
            "heartbeat_retry_seconds": 10,
            "server_extension_default_kernel_name": "pysparkkernel",
            "custom_headers": {},
            "retry_policy": "configurable",
            "retry_seconds_to_sleep_list": [0.2, 0.5, 1, 3, 5],
            "configurable_retry_policy_max_retries": 8
        }

    def on_create(self):
        script=[
            '#!/bin/bash',
            'set -e',
            'FILE="/home/ec2-user/.sparkmagic/config.json"',
            'sudo /bin/cat <<EOM >$FILE',
            json.dump(self._spark_magic_config(), Indent=4)
            'EOM'
        ]
        return "\n".join(script)

    def on_start(self):
        return ""
    
    def boot(self):
        pass
"""

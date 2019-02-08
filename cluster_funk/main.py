import os
import uuid

from tinydb import TinyDB
from cement import App, TestApp, init_defaults
from cement.ext.ext_logging import LoggingLogHandler 
from cement.core.exc import CaughtSignal
from cement.utils import fs
from cement.core.template import TemplateHandler
from jinja2 import Template
from .core.exc import ClusterFunkError
from .controllers.base import Base
from .controllers.clusters import Clusters
from .controllers.user_id import UserId
from .controllers.environments import Environments
from .controllers.jobs import Jobs

# configuration defaults
CONFIG = init_defaults('cluster_funk')
CONFIG['cluster_funk']['db_file'] = '~/.cluster_funk/db.json'


class CustomTemplateHandler(TemplateHandler):

    class Meta:
        label = "withcopy"

    def render(self, content, data):
        template = Template(content)
        return template.render(**data) 

def extend_tinydb(app):
    app.log.info('extending cluster_funk application with tinydb')
    db_file = app.config.get('cluster_funk', 'db_file')

    db_file = fs.abspath(db_file)
    app.log.info('tinydb database file is: %s' % db_file)

    db_dir = os.path.dirname(db_file)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    db = TinyDB(db_file)

    user_info = { 'id': str(uuid.uuid4())}
    table = db.table('users')
    allusers = table.all()
    if not len(allusers):
       table.insert(user_info)
    else:
       user_info = allusers[0]

    app.extend('db', db)

class ClusterFunk(App):
    """Cluster Funk primary application."""

    class Meta:
        label = 'cluster_funk'

        hooks = [
            ('post_setup', extend_tinydb)
        ]

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        close_on_exit = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
        ]

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'jinja2'

        template_handler = CustomTemplateHandler

        # register handlers
        handlers = [
            Base,
            Clusters,
            UserId,
            Environments,
            Jobs
        ]


class ClusterFunkTestLoggingLogHandler(LoggingLogHandler):
    pass


class ClusterFunkTest(TestApp,ClusterFunk):
    """A sub-class of ClusterFunk that is better suited for testing."""

    class Meta:
        label = 'cluster_funk'
        log_handler = ClusterFunkTestLoggingLogHandler

def main():
    with ClusterFunk() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except ClusterFunkError as e:
            print('ClusterFunkError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()

import os

from cement import Controller, ex
from cement.utils import fs
from cement.utils.version import get_version_banner
from ..core.version import get_version

VERSION_BANNER = """
cluster_funk - a CLI for developing big data jobs %s
%s
""" % (get_version(), get_version_banner())

class Base(Controller):
    class Meta:
        label = 'base'

        # text displayed at the top of --help output
        description = 'Cli for managing EMR clusters for big data'

        # text displayed at the bottom of --help output
        epilog = 'Usage: cluster_funk new my_project_name'

        # controller level arguments. ex: 'cluster_funk --version'
        arguments = [
            ### add a version banner
            ( [ '-v', '--version' ],
              { 'action'  : 'version',
                'version' : VERSION_BANNER } ),
        ]


    def _default(self):
        """Default action if no sub-command is passed."""
        self.app.args.print_help()

    @ex(
        help='Create a new cluster_funk project',
        arguments=[
            (['name'], { 'help': "what's the name of the project" })
        ]
    )
    def new(self):
        """Initialize EMR big data job project"""
        src = os.path.join(fs.abspath(__file__), os.pardir, os.pardir, "templates", "base")
        dest = os.path.join(os.curdir, self.app.pargs.name)
        self.app.template.copy(src, dest, {})


from setuptools import setup, find_packages
from cluster_funk.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='cluster_funk',
    version=VERSION,
    description='CLI for managing EMR clusters for big data',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Jeff Durand',
    author_email='jeff.durand@gmail.com',
    url='https://bitbucket.org/jeffdurand/cluster_funk',
    license='unlicensed',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'cluster_funk': ['templates/*']},
    include_package_data=True,
    install_requires=[
        "tinydb",
        "boto3",
        "colorlog",
        "jinja2",
        "fabric"
    ],
    entry_points="""
        [console_scripts]
        cluster_funk = cluster_funk.main:main
    """,
)

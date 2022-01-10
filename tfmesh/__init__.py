import click
from tfmesh.core import *

@click.group()
@click.version_option()
def cli():
    pass


@cli.group('get')
def get():
    """
    Terraform Mesh "get" command group.
    """
    pass


@get.command('terraform')
@click.option('-v', '--version', is_flag=True)
def terraform(version):
    """
    Get details about Terraform.
    """
    files = get_terraform_files("terraform")
    dependencies = get_dependencies(files)

    for dependency in dependencies:
        if dependency["target"] == "terraform":
            print(dependency["version"])
            return dependency["version"]

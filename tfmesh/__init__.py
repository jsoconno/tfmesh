import click
from pathlib import Path
import sys
from tfmesh.core import *

class Workspace:
    def __init__(self, terraform_folder, terraform_file_pattern):
        self.terraform_folder = terraform_folder
        self.terraform_file_pattern = terraform_file_pattern

    def __str__(self):
        return f'folder: {self.terraform_folder}  file_pattern: {self.terraform_file_pattern}'

def workspace_options(func):
    @click.option("--terraform-folder", default="")
    @click.option("--terraform-file-pattern", default="*.tf")
    def distill_workspace(terraform_folder, terraform_file_pattern, **kwargs):
        kwargs['workspace'] = Workspace(terraform_folder, terraform_file_pattern)
        func(**kwargs)

    return distill_workspace

@click.group("cli", invoke_without_command=True)
@click.version_option()
def cli(): # workspace):
    pass

@cli.group("get")
def get():
    """
    Gets attributes for a given resource.
    """
    pass

@cli.group("set")
def set():
    """
    Sets attributes for a given resource.
    """
    pass

@cli.group("test")
def test():
    """
    Used for testing purposes.
    """
    pass

@test.command("something")
@workspace_options
def something(workspace):
    click.echo(workspace.terraform_folder)

@get.command("terraform")
@click.argument("attribute", required=False)
@click.option("--allowed", is_flag=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--top", type=int, default=None)
@click.option("--var", multiple=True)
@workspace_options
def terraform(workspace, attribute, allowed, exclude_prerelease, top, var):
    """
    Gets a given attribute for the Terraform executable.
    """
    is_valid = validate_attribute(attribute, options("GET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = get_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=workspace.terraform_folder,
            file_pattern=workspace.terraform_file_pattern
        ),
        patterns={
            "terraform": [patterns("TERRAFORM")]
        },
        resource_type = "terraform",
        name="terraform",
        attribute=attribute,
        allowed=allowed,
        exclude_prerelease=exclude_prerelease,
        top=top
    )
    click.echo(result)

@get.command("providers")
@workspace_options
def providers(workspace):
    """
    Lists all tracked providers.
    """
    resources = get_resources(
        terraform_files=get_terraform_files(
            terraform_folder=workspace.terraform_folder,
            file_pattern=workspace.terraform_file_pattern
        ),
        patterns={
            "providers": [patterns("PROVIDER")],
        }
    )
    click.echo(resources)

@get.command("provider")
@click.argument("name", type=str)
@click.argument("attribute", required=False)
@click.option("--allowed", is_flag=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--top", type=int, default=None)
@click.option("--var", multiple=True)
@workspace_options
def provider(workspace, name, attribute, allowed, exclude_prerelease, top, var):
    """
    Gets a given attribute for provider.
    """
    is_valid = validate_attribute(attribute, options("GET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = get_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=workspace.terraform_folder,
            file_pattern=workspace.terraform_file_pattern
        ),
        patterns={
            "providers": [patterns("PROVIDER")],
        },
        resource_type = "providers",
        name=name,
        attribute=attribute,
        allowed=allowed,
        exclude_prerelease=exclude_prerelease,
        top=top
    )
    click.echo(result)

@get.command("modules")
@workspace_options
def modules(workspace):
    """
    Lists all tracked modules.
    """
    resources = get_resources(
        terraform_files=get_terraform_files(
            terraform_folder=workspace.terraform_folder,
            file_pattern=workspace.terraform_file_pattern
        ),
        patterns={
            "modules": [
                patterns("MODULE_REGISTRY"),
                patterns("MODULE_GITHUB"),
            ],
        }
    )
    click.echo(resources)

@get.command("module")
@click.argument("name", type=str)
@click.argument("attribute", required=False)
@click.option("--allowed", is_flag=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--top", type=int, default=None)
@click.option("--var", multiple=True)
@workspace_options
def module(workspace, name, attribute, allowed, exclude_prerelease, top, var):
    """
    Gets a given attribute for module.
    """
    is_valid = validate_attribute(attribute, options("GET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = get_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=workspace.terraform_folder,
            file_pattern=workspace.terraform_file_pattern
        ),
        patterns={
            "modules": [
                patterns("MODULE_REGISTRY"),
                patterns("MODULE_GITHUB"),
            ],
        },
        resource_type = "modules",
        name=name,
        attribute=attribute,
        allowed=allowed,
        exclude_prerelease=exclude_prerelease,
        top=top
    )
    click.echo(result)

@set.command("terraform")
@click.argument("attribute", required=False)
@click.argument("value")
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--what-if", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--var", multiple=True)
@click.option("--force", is_flag=True)
@workspace_options
def terraform(workspace, attribute, value, exclude_prerelease, what_if, ignore_constraints, var, force):
    """
    Sets the version or constraint for the Terraform executable.
    """
    is_valid = validate_attribute(attribute, options("SET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = set_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=workspace.terraform_folder,
            file_pattern=workspace.terraform_file_pattern
        ),
        patterns={
            "terraform": [patterns("TERRAFORM")],
        },
        resource_type = "terraform",
        name="terraform",
        attribute=attribute,
        value=value,
        exclude_prerelease=exclude_prerelease,
        what_if=what_if,
        ignore_constraints=ignore_constraints,
        force=force
    )
    click.echo(result)

@set.command("provider")
@click.argument("name", type=str)
@click.argument("attribute", required=False)
@click.argument("value")
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--what-if", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--var", multiple=True)
@click.option("--force", is_flag=True)
@workspace_options
def provider(workspace, name, attribute, value, exclude_prerelease, what_if, ignore_constraints, var, force):
    """
    Sets the version or constraint for a given provider.
    """
    is_valid = validate_attribute(attribute, options("SET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = set_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=workspace.terraform_folder,
            file_pattern=workspace.terraform_file_pattern
        ),
        patterns={
            "providers": [patterns("PROVIDER")],
        },
        resource_type = "providers",
        name=name,
        attribute=attribute,
        value=value,
        exclude_prerelease=exclude_prerelease,
        what_if=what_if,
        ignore_constraints=ignore_constraints,
        force=force
    )
    click.echo(result)

@set.command("module")
@click.argument("name", type=str)
@click.argument("attribute", required=False)
@click.argument("value")
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--what-if", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--var", multiple=True)
@click.option("--force", is_flag=True)
@workspace_options
def module(workspace, name, attribute, value, exclude_prerelease, what_if, ignore_constraints, var, force):
    """
    Sets the version or constraint for a given module.
    """
    is_valid = validate_attribute(attribute, options("SET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = set_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=workspace.terraform_folder,
            file_pattern=workspace.terraform_file_pattern
        ),
        patterns={
            "modules": [
                patterns("MODULE_REGISTRY"),
                patterns("MODULE_GITHUB"),
            ],
        },
        resource_type = "modules",
        name=name,
        attribute=attribute,
        value=value,
        exclude_prerelease=exclude_prerelease,
        what_if=what_if,
        ignore_constraints=ignore_constraints,
        force=force
    )
    click.echo(result)

@cli.command("plan")
@click.option("--target", nargs=2, multiple=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--no-color", is_flag=True)
@click.option("--verbose", is_flag=True)
@click.option("--var", multiple=True)
@workspace_options
def plan(workspace, target, exclude_prerelease, ignore_constraints, no_color, verbose, var):
    """
    Plans what version changes will be made to the configuration.
    """
    set_environment_variables(var)
    run_plan_apply(
        terraform_files=get_terraform_files(
            terraform_folder=workspace.terraform_folder,
            file_pattern=workspace.terraform_file_pattern
        ),
        patterns = {
            "terraform": [patterns("TERRAFORM")],
            "providers": [patterns("PROVIDER")],
            "modules": [
                patterns("MODULE_REGISTRY"),
                patterns("MODULE_GITHUB")
            ]
        },
        target=target,
        verbose=verbose,
        exclude_prerelease=exclude_prerelease,
        ignore_constraints=ignore_constraints,
        no_color=no_color
    )

@cli.command("apply")
@click.option("--target", nargs=2, multiple=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--no-color", is_flag=True)
@click.option("--verbose", is_flag=True)
@click.option("--auto-approve", is_flag=True)
@click.option("--var", multiple=True)
@click.pass_obj
def apply(config, target, exclude_prerelease, ignore_constraints, no_color, verbose, auto_approve, var):
    """
    Applies configuration version changes.
    """
    set_environment_variables(var)
    run_plan_apply(
        terraform_files=config["terraform_files"],
        patterns = {
            "terraform": [patterns("TERRAFORM")],
            "providers": [patterns("PROVIDER")],
            "modules": [
                patterns("MODULE_REGISTRY"),
                patterns("MODULE_GITHUB")
            ]
        },
        apply=True,
        target=target,
        verbose=verbose,
        exclude_prerelease=exclude_prerelease,
        ignore_constraints=ignore_constraints,
        no_color=no_color
    )
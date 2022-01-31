import click
from pathlib import Path
import sys
from tfmesh.core import *

CONTEXT_SETTINGS = dict(auto_envvar_prefix='TFMESH')

def workspace_options(f):
    f = click.option("--terraform-folder", default="", help="The name of the folder where Terraform files are located (defaults to the current directory).")(f)
    f = click.option("--terraform-file-pattern", default="*.tf", help="The pattern for matching Terraform files within the directory (defaults to *.tf).")(f)
    f = click.option("--var", multiple=True, help="One or more variables to be set as environment variables in the format 'some=value'.")(f)

    return f

def get_options(f):
    f = click.argument("attribute", required=False)(f)
    f = click.option("--allowed", is_flag=True, help="Returns only allowed versions when used in conjunction with the versions attribute.")(f)
    f = click.option("--exclude-prerelease", is_flag=True, help="Returns all non-prerelease versions when used in conjunction with the versions attribute.")(f)
    f = click.option("--top", type=int, default=None, help="Returns the top n number of results when used in conjunction with the versions attribute.")(f)

    return f

def set_options(f):
    f = click.argument("value")(f)
    f = click.argument("attribute", required=False)(f)
    f = click.option("--exclude-prerelease", is_flag=True, help="Ensures the set version is not a pre-release.")(f)
    f = click.option("--ignore-constraints", is_flag=True, help="Allows the version to be set to a valid version that does not meet the defined constraint.")(f)
    f = click.option("--what-if", is_flag=True, help="Allows for a dry run to see what would happen before making changes.")(f)
    f = click.option("--force", is_flag=True, help="Allows the version to be set to any value without validation.")(f)

    return f

def plan_apply_options(f):
    f = click.option("--target", nargs=2, multiple=True, help="Takes arguments `TYPE` and `NAME` to allow for specific update targets.  For example, `--target provider aws`.  Multiple targets are allowed.")(f)
    f = click.option("--exclude-prerelease", is_flag=True, help="Ensures the set version is not a pre-release.")(f)
    f = click.option("--ignore-constraints", is_flag=True, help="Allows the version to be set to a valid version that does not meet the defined constraint.")(f)
    f = click.option("--no-color", is_flag=True, help="Removes terminal color formatting, primarily for automation purposes.")(f)
    f = click.option("--verbose", is_flag=True, help="Returns all resources including those with no version changes.")(f)
    
    return f

@click.group("cli", invoke_without_command=True)
@click.version_option()
def cli():
    """
    \b
    A mesh is an interlaced structure. A network of interconnected things. 
    As a verb, it can mean to be locked together or engaged with another. 
    
    Terraform Mesh CLI (or tfmesh for short) is an open source tool designed 
    to make Terraform version management simple and effective.

    It allows you to get details about versioned Terraform resources in your
    configuration, set values for versions and constraints, and automatically
    make updates to your code so you are always up-to-date.
    
    It supports all Terraform native version constraint operators as well
    as public and private sources for providers and modules.
    """
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

@get.command(context_settings=CONTEXT_SETTINGS)
@get_options
@workspace_options
def terraform(terraform_file_pattern, terraform_folder, attribute, allowed, exclude_prerelease, top, var):
    """
    Gets a given attribute for the Terraform executable.
    """
    is_valid = validate_attribute(attribute, options("GET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = get_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=terraform_folder,
            file_pattern=terraform_file_pattern
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

@get.command(context_settings=CONTEXT_SETTINGS)
@workspace_options
def providers(terraform_file_pattern, terraform_folder, var):
    """
    Lists all tracked providers.
    """
    resources = get_resources(
        terraform_files=get_terraform_files(
            terraform_folder=terraform_folder,
            file_pattern=terraform_file_pattern
        ),
        patterns={
            "providers": [patterns("PROVIDER")],
        }
    )
    click.echo(resources)

@get.command(context_settings=CONTEXT_SETTINGS)
@click.argument("name", type=str)
@get_options
@workspace_options
def provider(terraform_file_pattern, terraform_folder, name, attribute, allowed, exclude_prerelease, top, var):
    """
    Gets a given attribute for provider.
    """
    is_valid = validate_attribute(attribute, options("GET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = get_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=terraform_folder,
            file_pattern=terraform_file_pattern
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

@get.command(context_settings=CONTEXT_SETTINGS)
@workspace_options
def modules(terraform_file_pattern, terraform_folder, var):
    """
    Lists all tracked modules.
    """
    resources = get_resources(
        terraform_files=get_terraform_files(
            terraform_folder=terraform_folder,
            file_pattern=terraform_file_pattern
        ),
        patterns={
            "modules": [
                patterns("MODULE_REGISTRY"),
                patterns("MODULE_GITHUB"),
            ],
        }
    )
    click.echo(resources)

@get.command(context_settings=CONTEXT_SETTINGS)
@click.argument("name", type=str)
@get_options
@workspace_options
def module(terraform_file_pattern, terraform_folder, name, attribute, allowed, exclude_prerelease, top, var):
    """
    Gets a given attribute for module.
    """
    is_valid = validate_attribute(attribute, options("GET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = get_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=terraform_folder,
            file_pattern=terraform_file_pattern
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

@set.command(context_settings=CONTEXT_SETTINGS)
@set_options
@workspace_options
def terraform(terraform_file_pattern, terraform_folder, attribute, value, exclude_prerelease, what_if, ignore_constraints, var, force):
    """
    Sets the version or constraint for the Terraform executable.
    """
    is_valid = validate_attribute(attribute, options("SET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = set_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=terraform_folder,
            file_pattern=terraform_file_pattern
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

@set.command(context_settings=CONTEXT_SETTINGS)
@click.argument("name", type=str)
@set_options
@workspace_options
def provider(terraform_file_pattern, terraform_folder, name, attribute, value, exclude_prerelease, what_if, ignore_constraints, var, force):
    """
    Sets the version or constraint for a given provider.
    """
    is_valid = validate_attribute(attribute, options("SET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = set_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=terraform_folder,
            file_pattern=terraform_file_pattern
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

@set.command(context_settings=CONTEXT_SETTINGS)
@click.argument("name", type=str)
@set_options
@workspace_options
def module(terraform_file_pattern, terraform_folder, name, attribute, value, exclude_prerelease, what_if, ignore_constraints, var, force):
    """
    Sets the version or constraint for a given module.
    """
    is_valid = validate_attribute(attribute, options("SET"))
    if not is_valid:
        sys.exit()
    set_environment_variables(var)
    result = set_dependency_attribute(
        terraform_files=get_terraform_files(
            terraform_folder=terraform_folder,
            file_pattern=terraform_file_pattern
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

@cli.command(context_settings=CONTEXT_SETTINGS)
@plan_apply_options
@workspace_options
def plan(terraform_file_pattern, terraform_folder, target, exclude_prerelease, ignore_constraints, no_color, verbose, var):
    """
    Plans what version changes will be made to the configuration.
    """
    set_environment_variables(var)
    run_plan_apply(
        terraform_files=get_terraform_files(
            terraform_folder=terraform_folder,
            file_pattern=terraform_file_pattern
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

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--auto-approve", is_flag=True)
@plan_apply_options
@workspace_options
def apply(terraform_file_pattern, terraform_folder, target, exclude_prerelease, ignore_constraints, no_color, verbose, auto_approve, var):
    """
    Applies configuration version changes.
    """
    set_environment_variables(var)
    run_plan_apply(
        terraform_files=get_terraform_files(
            terraform_folder=terraform_folder,
            file_pattern=terraform_file_pattern
        ),
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
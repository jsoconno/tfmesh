import click
from pathlib import Path
import sys
from tfmesh.core import *

CONTEXT_SETTINGS = dict(auto_envvar_prefix='TFMESH')

def workspace_options(f):
    f = click.option("--terraform-folder", default="")(f)
    f = click.option("--terraform-file-pattern", default="*.tf")(f)

    return f

def get_options(f):
    f = click.argument("attribute", required=False)(f)
    f = click.option("--allowed", is_flag=True)(f)
    f = click.option("--exclude-prerelease", is_flag=True)(f)
    f = click.option("--top", type=int, default=None)(f)
    f = click.option("--var", multiple=True)(f)
    # f = click.option("--github_token", default=None)(f)

    return f

def set_options(f):
    f = click.argument("value")(f)
    f = click.argument("attribute", required=False)(f)
    f = click.option("--exclude-prerelease", is_flag=True)(f)
    f = click.option("--what-if", is_flag=True)(f)
    f = click.option("--ignore-constraints", is_flag=True)(f)
    f = click.option("--var", multiple=True)(f)
    f = click.option("--force", is_flag=True)(f)

    return f

def plan_apply_options(f):
    f = click.option("--target", nargs=2, multiple=True)(f)
    f = click.option("--exclude-prerelease", is_flag=True)(f)
    f = click.option("--ignore-constraints", is_flag=True)(f)
    f = click.option("--no-color", is_flag=True)(f)
    f = click.option("--verbose", is_flag=True)(f)
    f = click.option("--var", multiple=True)(f)
    
    return f

@click.group("cli", invoke_without_command=True)
@click.version_option()
def cli():
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

@cli.command(context_settings=CONTEXT_SETTINGS)
@workspace_options
@get_options
def test(terraform_file_pattern, terraform_folder, attribute, allowed, exclude_prerelease, top, github_token):
    click.echo(terraform_file_pattern)
    click.echo(attribute)

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
def providers(terraform_file_pattern, terraform_folder):
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
def modules(terraform_file_pattern, terraform_folder):
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
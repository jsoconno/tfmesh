import click
from pathlib import Path
import os
import re
import requests
import json
import operator
import yaml
from tfmesh.core import *

choices = {
    "GET": ["target", "filepath", "filename", "code", "name", "source", "version", "versions", "constraint", "lower_constraint_operator", "lower_constraint", "upper_constraint_operator", "upper_constraint"],
    "SET": ["version", "constraint"]
}

@click.group("cli", invoke_without_command=True)
@click.version_option()
@click.pass_context
def cli(ctx):
    config = get_config()
    
    if config == None:
        config = {"terraform_files": get_terraform_files()}

    ctx.obj = config

@cli.command("init")
@click.option("--config-file", default=".tfmesh.yaml")
@click.option("--terraform-folder", default="")
@click.option("--terraform-file-pattern", default="*.tf")
@click.option("--var", multiple=True)
@click.option("--force", is_flag=True)
def init(config_file, terraform_folder, terraform_file_pattern, var, force):
    """
    Initializes a file with details about the configuration.
    """
    config_file = Path(config_file)
    if config_file.is_file():
        if force:
            set_config(config_file, terraform_folder, terraform_file_pattern, var)
            click.echo("The configuration was updated.")
        else:
            if click.confirm("A configuration file already exists.  Would you like to update it?"):
                set_config(config_file, terraform_folder, terraform_file_pattern, var)
                click.echo("The configuration was updated.")
            else:
                click.echo("The configuration was not changed.")
    else:
        set_config(config_file, terraform_folder, terraform_file_pattern, var)
        click.echo("The configuration was created.")

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

@get.command("terraform")
@click.argument("attribute", required=False)
@click.option("--allowed", is_flag=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--top", type=int, default=None)
@click.option("--var", multiple=True)
@click.pass_obj
def terraform(config, attribute, allowed, exclude_prerelease, top, var):
    """
    Gets a given attribute for the Terraform executable.
    """
    is_valid = validate_attribute(attribute, choices["GET"])
    if not is_valid:
        raise click.Abort()
    set_environment_variables(var)
    result = get_dependency_attribute(
        terraform_files=config["terraform_files"],
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
@click.pass_obj
def providers(config):
    """
    Lists all tracked providers.
    """
    resources = get_resources(
        terraform_files=config["terraform_files"],
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
@click.pass_obj
def provider(config, name, attribute, allowed, exclude_prerelease, top, var):
    """
    Gets a given attribute for provider.
    """
    is_valid = validate_attribute(attribute, choices["GET"])
    if not is_valid:
        raise click.Abort()
    set_environment_variables(var)
    result = get_dependency_attribute(
        terraform_files=config["terraform_files"],
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
@click.pass_obj
def modules(config):
    """
    Lists all tracked modules.
    """
    resources = get_resources(
        terraform_files=config["terraform_files"],
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
@click.pass_obj
def module(config, name, attribute, allowed, exclude_prerelease, top, var):
    """
    Gets a given attribute for module.
    """
    is_valid = validate_attribute(attribute, choices["GET"])
    if not is_valid:
        raise click.Abort()
    set_environment_variables(var)
    result = get_dependency_attribute(
        terraform_files=config["terraform_files"],
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
@click.pass_obj
def terraform(config, attribute, value, exclude_prerelease, what_if, ignore_constraints, var, force):
    """
    Sets the version or constraint for the Terraform executable.
    """
    is_valid = validate_attribute(attribute, choices["SET"])
    if not is_valid:
        raise click.Abort()
    set_environment_variables(var)
    result = set_dependency_attribute(
        terraform_files=config["terraform_files"],
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
@click.pass_obj
def provider(config, name, attribute, value, exclude_prerelease, what_if, ignore_constraints, var, force):
    """
    Sets the version or constraint for a given provider.
    """
    is_valid = validate_attribute(attribute, choices["SET"])
    if not is_valid:
        raise click.Abort()
    set_environment_variables(var)
    result = set_dependency_attribute(
        terraform_files=config["terraform_files"],
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
@click.pass_obj
def module(config, name, attribute, value, exclude_prerelease, what_if, ignore_constraints, var, force):
    """
    Sets the version or constraint for a given module.
    """
    is_valid = validate_attribute(attribute, choices["SET"])
    if not is_valid:
        raise click.Abort()
    set_environment_variables(var)
    result = set_dependency_attribute(
        terraform_files=config["terraform_files"],
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
@click.pass_obj
def plan(config, target, exclude_prerelease, ignore_constraints, no_color, verbose, var):
    """
    Plans what version changes will be made to the configuration.
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
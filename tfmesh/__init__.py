import click
from pathlib import Path
import os
import re
import requests
import json
import operator
import yaml
from tfmesh.core import *

@click.group("cli", invoke_without_command=True)
@click.pass_context
def cli(ctx):
    ctx.obj = get_config()

@cli.command("init")
@click.option("--config-file", default=".tfmesh.yaml")
@click.option("--terraform-folder", default="")
@click.option("--terraform-file-pattern", default="*.tf")
@click.option("--force", is_flag=True)
def init(config_file, terraform_folder, terraform_file_pattern, force):
    config_file = Path(config_file)
    if config_file.is_file():
        if force:
            set_config(config_file, terraform_folder, terraform_file_pattern)
            print("The configuration was updated.")
        if click.confirm("A configuration file already exists.  Would you like to update it?"):
            set_config(config_file, terraform_folder, terraform_file_pattern)
            print("The configuration was updated.")
        else:
            print("The configuration was not changed.")
    else:
        set_config(config_file, terraform_folder, terraform_file_pattern)
        print("The configuration was created.")

@cli.group("get")
def get():
    pass

@cli.group("set")
def set():
    pass

@get.command("terraform")
@click.argument("attribute", type=click.Choice(["target", "filepath", "filename", "code", "name", "source", "version", "versions", "constraint", "lower_constraint_operator", "lower_constraint", "upper_constraint_operator", "upper_constraint"]))
@click.option("--allowed", is_flag=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--top", type=int, default=None)
@click.pass_obj
def terraform(config, attribute, allowed, exclude_prerelease, top):
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "terraform": [r'(((terraform)) *{[^}]*?required_version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?)'],
        }
    )
    available_versions = sort_versions(
        get_available_versions(
            target=dependencies["terraform"]["terraform"]["target"],
            source=dependencies["terraform"]["terraform"]["source"],
            exclude_pre_release=exclude_prerelease
        )
    )
    allowed_versions = sort_versions(
        get_allowed_versions(
            available_versions,
            dependencies["terraform"]["terraform"]["lower_constraint"],
            dependencies["terraform"]["terraform"]["lower_constraint_operator"],
            dependencies["terraform"]["terraform"]["upper_constraint"],
            dependencies["terraform"]["terraform"]["upper_constraint_operator"],
        )
    )
    if attribute == "versions":
        if allowed:
            print_list(allowed_versions, top)
        else:
            print_list(available_versions, top)
    else:
        print(dependencies["terraform"]["terraform"][attribute])

@get.command("providers")
@click.pass_obj
def providers(config):
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "provider": [r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'],
        }
    )
    for resource_type, providers in dependencies.items():
        for provider in providers:
            print(f'- {provider}')

@get.command("provider")
@click.argument("name", type=str)
@click.argument("attribute", type=click.Choice(["target", "filepath", "filename", "code", "name", "source", "version", "versions", "constraint", "lower_constraint_operator", "lower_constraint", "upper_constraint_operator", "upper_constraint"]))
@click.option("--allowed", is_flag=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--top", type=int, default=None)
@click.pass_obj
def provider(config, name, attribute, allowed, exclude_prerelease, top):
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "provider": [r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'],
        }
    )
    available_versions = sort_versions(
        get_available_versions(
            target=dependencies["provider"][name]["target"],
            source=dependencies["provider"][name]["source"],
            exclude_pre_release=exclude_prerelease
        )
    )
    allowed_versions = sort_versions(
        get_allowed_versions(
            available_versions,
            dependencies["provider"][name]["lower_constraint"],
            dependencies["provider"][name]["lower_constraint_operator"],
            dependencies["provider"][name]["upper_constraint"],
            dependencies["provider"][name]["upper_constraint_operator"],
        )
    )
    if attribute == "versions":
        if allowed:
            print_list(allowed_versions, top)
        else:
            print_list(available_versions, top)
    else:
        print(dependencies["provider"][name][attribute])

@get.command("modules")
@click.pass_obj
def modules(config):
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "module": [
                r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
                r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\?ref=([a-zA-Z]*\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
            ],
        }
    )
    for resource_type, modules in dependencies.items():
        for module in modules:
            print(f'- {module}')

@get.command("module")
@click.argument("name", type=str)
@click.argument("attribute", type=click.Choice(["target", "filepath", "filename", "code", "name", "source", "version", "versions", "constraint", "lower_constraint_operator", "lower_constraint", "upper_constraint_operator", "upper_constraint"]))
@click.option("--allowed", is_flag=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--top", type=int, default=None)
@click.pass_obj
def module(config, name, attribute, allowed, exclude_prerelease, top):
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "module": [
                r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
                r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\?ref=([a-zA-Z]*\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
            ],
        }
    )
    available_versions = sort_versions(get_available_versions(
        target=dependencies["module"][name]["target"],
        source=dependencies["module"][name]["source"],
        exclude_pre_release=exclude_prerelease)
    )
    allowed_versions = sort_versions(
        get_allowed_versions(
            available_versions,
            dependencies["module"][name]["lower_constraint"],
            dependencies["module"][name]["lower_constraint_operator"],
            dependencies["module"][name]["upper_constraint"],
            dependencies["module"][name]["upper_constraint_operator"],
        )
    )
    if attribute == "versions":
        if allowed:
            print_list(allowed_versions, top)
        else:
            print_list(available_versions, top)
    else:
        print(dependencies["module"][name][attribute])

@set.command("terraform")
@click.argument("attribute", type=click.Choice(["version", "constraint"]))
@click.argument("value")
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--what-if", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--force", is_flag=True)
@click.pass_obj
def terraform(config, attribute, value, exclude_prerelease, what_if, ignore_constraints, force):
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "terraform": [r'(((terraform)) *{[^}]*?required_version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?)'],
        }
    )
    available_versions = sort_versions(
        get_available_versions(
            target=dependencies["terraform"]["terraform"]["target"],
            source=dependencies["terraform"]["terraform"]["source"],
            exclude_pre_release=exclude_prerelease
        )
    )
    allowed_versions = sort_versions(
        get_allowed_versions(
            available_versions,
            dependencies["terraform"]["terraform"]["lower_constraint"],
            dependencies["terraform"]["terraform"]["lower_constraint_operator"],
            dependencies["terraform"]["terraform"]["upper_constraint"],
            dependencies["terraform"]["terraform"]["upper_constraint_operator"],
        )
    )
    current_value = dependencies["terraform"]["terraform"][attribute]
    new_value = value

    if ignore_constraints:
        versions = available_versions
    else:
        versions = allowed_versions

    if current_value == new_value:
        print(f'The {attribute} is already set to "{new_value}".')
    elif force or new_value in versions or attribute == "constraint":
        update_version(
            filepath=dependencies["terraform"]["terraform"]["filepath"],
            code=dependencies["terraform"]["terraform"]["code"],
            attribute=attribute,
            value=value
        )
        print(f'The {attribute} was changed from "{current_value}" to "{new_value}".')
    elif versions == []:
        print(f'There is no version available that meets the constraint "{dependencies["terraform"]["terraform"]["constraint"]}".')
    else:
        print(f'"{value}" is not an acceptable version.  Select from one of:')
        print_list(versions)
        raise click.Abort

@set.command("provider")
@click.argument("name", type=str)
@click.argument("attribute", type=click.Choice(["version", "constraint"]))
@click.argument("value")
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--what-if", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--force", is_flag=True)
@click.pass_obj
def provider(config, name, attribute, value, exclude_prerelease, what_if, ignore_constraints, force):
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "provider": [r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'],
        }
    )
    available_versions = sort_versions(
        get_available_versions(
            target=dependencies["provider"][name]["target"],
            source=dependencies["provider"][name]["source"],
            exclude_pre_release=exclude_prerelease
        )
    )
    allowed_versions = sort_versions(
        get_allowed_versions(
            available_versions,
            dependencies["provider"][name]["lower_constraint"],
            dependencies["provider"][name]["lower_constraint_operator"],
            dependencies["provider"][name]["upper_constraint"],
            dependencies["provider"][name]["upper_constraint_operator"],
        )
    )
    current_value = dependencies["provider"][name][attribute]
    new_value = value

    if ignore_constraints:
        versions = available_versions
    else:
        versions = allowed_versions

    if current_value == new_value:
        print(f'The {attribute} is already set to "{new_value}".')
    elif force or new_value in versions or attribute == "constraint":
        update_version(
            filepath=dependencies["provider"][name]["filepath"],
            code=dependencies["provider"][name]["code"],
            attribute=attribute,
            value=value
        )
        print(f'The {attribute} was changed from "{current_value}" to "{new_value}".')
    elif versions == []:
        print(f'There is no version available that meets the constraint "{dependencies["provider"][name]["constraint"]}".')
    else:
        print(f'"{value}" is not an acceptable version.  Select from one of:')
        print_list(versions)
        raise click.Abort

@set.command("module")
@click.argument("name", type=str)
@click.argument("attribute", type=click.Choice(["version", "constraint"]))
@click.argument("value")
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--what-if", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--force", is_flag=True)
@click.pass_obj
def module(config, name, attribute, value, exclude_prerelease, what_if, ignore_constraints, force):
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "module": [
                r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
                r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\?ref=([a-zA-Z]*\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
            ],
        }
    )
    available_versions = sort_versions(
        get_available_versions(
            target=dependencies["module"][name]["target"],
            source=dependencies["module"][name]["source"],
            exclude_pre_release=exclude_prerelease
        )
    )
    allowed_versions = sort_versions(
        get_allowed_versions(
            available_versions,
            dependencies["module"][name]["lower_constraint"],
            dependencies["module"][name]["lower_constraint_operator"],
            dependencies["module"][name]["upper_constraint"],
            dependencies["module"][name]["upper_constraint_operator"],
        )
    )
    current_value = dependencies["module"][name][attribute]
    new_value = value

    if ignore_constraints:
        versions = available_versions
    else:
        versions = allowed_versions

    if current_value == new_value:
        print(f'The {attribute} is already set to "{new_value}".')
    elif force or new_value in versions or attribute == "constraint":
        update_version(
            filepath=dependencies["module"][name]["filepath"],
            code=dependencies["module"][name]["code"],
            attribute=attribute,
            value=value
        )
        print(f'The {attribute} was changed from "{current_value}" to "{new_value}".')
    elif versions == []:
        print(f'There is no version available that meets the constraint "{dependencies["module"][name]["constraint"]}".')
    else:
        print(f'"{value}" is not an acceptable version.  Select from one of:')
        print_list(versions)
        raise click.Abort

@cli.command("plan")
@click.pass_obj
def plan(config):
    pass
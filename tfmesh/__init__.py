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
@click.version_option()
@click.pass_context
def cli(ctx):
    ctx.obj = get_config()

@cli.command("init")
@click.option("--config-file", default=".tfmesh.yaml")
@click.option("--terraform-folder", default="")
@click.option("--terraform-file-pattern", default="*.tf")
@click.option("--force", is_flag=True)
def init(config_file, terraform_folder, terraform_file_pattern, force):
    """
    Initializes a file with details about the configuration.
    """
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
@click.argument("attribute", type=click.Choice(["target", "filepath", "filename", "code", "name", "source", "version", "versions", "constraint", "lower_constraint_operator", "lower_constraint", "upper_constraint_operator", "upper_constraint"]))
@click.option("--allowed", is_flag=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--top", type=int, default=None)
@click.pass_obj
def terraform(config, attribute, allowed, exclude_prerelease, top):
    """
    Gets a given attribute for the Terraform executable.
    """
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
    """
    Lists all tracked providers.
    """
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "providers": [r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'],
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
    """
    Gets a given attribute for provider.
    """
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "providers": [r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'],
        }
    )
    available_versions = sort_versions(
        get_available_versions(
            target=dependencies["providers"][name]["target"],
            source=dependencies["providers"][name]["source"],
            exclude_pre_release=exclude_prerelease
        )
    )
    allowed_versions = sort_versions(
        get_allowed_versions(
            available_versions,
            dependencies["providers"][name]["lower_constraint"],
            dependencies["providers"][name]["lower_constraint_operator"],
            dependencies["providers"][name]["upper_constraint"],
            dependencies["providers"][name]["upper_constraint_operator"],
        )
    )
    if attribute == "versions":
        if allowed:
            print_list(allowed_versions, top)
        else:
            print_list(available_versions, top)
    else:
        print(dependencies["providers"][name][attribute])

@get.command("modules")
@click.pass_obj
def modules(config):
    """
    Lists all tracked modules.
    """
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "modules": [
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
    """
    Gets a given attribute for module.
    """
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "modules": [
                r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
                r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\?ref=([a-zA-Z]*\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
            ],
        }
    )
    available_versions = sort_versions(get_available_versions(
        target=dependencies["modules"][name]["target"],
        source=dependencies["modules"][name]["source"],
        exclude_pre_release=exclude_prerelease)
    )
    allowed_versions = sort_versions(
        get_allowed_versions(
            available_versions,
            dependencies["modules"][name]["lower_constraint"],
            dependencies["modules"][name]["lower_constraint_operator"],
            dependencies["modules"][name]["upper_constraint"],
            dependencies["modules"][name]["upper_constraint_operator"],
        )
    )
    if attribute == "versions":
        if allowed:
            print_list(allowed_versions, top)
        else:
            print_list(available_versions, top)
    else:
        print(dependencies["modules"][name][attribute])

@set.command("terraform")
@click.argument("attribute", type=click.Choice(["version", "constraint"]))
@click.argument("value")
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--what-if", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--force", is_flag=True)
@click.pass_obj
def terraform(config, attribute, value, exclude_prerelease, what_if, ignore_constraints, force):
    """
    Sets the version or constraint for the Terraform executable.
    """
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
    """
    Sets the version or constraint for a given provider.
    """
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "providers": [r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'],
        }
    )
    available_versions = sort_versions(
        get_available_versions(
            target=dependencies["providers"][name]["target"],
            source=dependencies["providers"][name]["source"],
            exclude_pre_release=exclude_prerelease
        )
    )
    allowed_versions = sort_versions(
        get_allowed_versions(
            available_versions,
            dependencies["providers"][name]["lower_constraint"],
            dependencies["providers"][name]["lower_constraint_operator"],
            dependencies["providers"][name]["upper_constraint"],
            dependencies["providers"][name]["upper_constraint_operator"],
        )
    )
    current_value = dependencies["providers"][name][attribute]
    new_value = value

    if ignore_constraints:
        versions = available_versions
    else:
        versions = allowed_versions

    if current_value == new_value:
        print(f'The {attribute} is already set to "{new_value}".')
    elif force or new_value in versions or attribute == "constraint":
        update_version(
            filepath=dependencies["providers"][name]["filepath"],
            code=dependencies["providers"][name]["code"],
            attribute=attribute,
            value=value
        )
        print(f'The {attribute} was changed from "{current_value}" to "{new_value}".')
    elif versions == []:
        print(f'There is no version available that meets the constraint "{dependencies["providers"][name]["constraint"]}".')
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
    """
    Sets the version or constraint for a given module.
    """
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns={
            "modules": [
                r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
                r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\?ref=([a-zA-Z]*\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
            ],
        }
    )
    available_versions = sort_versions(
        get_available_versions(
            target=dependencies["modules"][name]["target"],
            source=dependencies["modules"][name]["source"],
            exclude_pre_release=exclude_prerelease
        )
    )
    allowed_versions = sort_versions(
        get_allowed_versions(
            available_versions,
            dependencies["modules"][name]["lower_constraint"],
            dependencies["modules"][name]["lower_constraint_operator"],
            dependencies["modules"][name]["upper_constraint"],
            dependencies["modules"][name]["upper_constraint_operator"],
        )
    )
    current_value = dependencies["modules"][name][attribute]
    new_value = value

    if ignore_constraints:
        versions = available_versions
    else:
        versions = allowed_versions

    if current_value == new_value:
        print(f'The {attribute} is already set to "{new_value}".')
    elif force or new_value in versions or attribute == "constraint":
        update_version(
            filepath=dependencies["modules"][name]["filepath"],
            code=dependencies["modules"][name]["code"],
            attribute=attribute,
            value=value
        )
        print(f'The {attribute} was changed from "{current_value}" to "{new_value}".')
    elif versions == []:
        print(f'There is no version available that meets the constraint "{dependencies["modules"][name]["constraint"]}".')
    else:
        print(f'"{value}" is not an acceptable version.  Select from one of:')
        print_list(versions)
        raise click.Abort

@cli.command("plan")
@click.option("--target", nargs=2, multiple=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--no-color", is_flag=True)
@click.pass_obj
def plan(config, target, exclude_prerelease, ignore_constraints, no_color):
    """
    Plans what version changes will be made to the configuration.
    """
    table_headers = ["resource\ntype", "module\nname", "current\nversion", "latest\navailable", "constraint", "latest\nallowed", "status"]
    table = []
    patterns = {
        "terraform": [r'(((terraform)) *{[^}]*?required_version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?)'],
        "providers": [r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'],
        "modules": [
            r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
            r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\?ref=([a-zA-Z]*\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})'
        ]
    }
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns = patterns
    )
    for resource_type, resource in dependencies.items():
        for name, attributes in resource.items():
            available_versions = sort_versions(
                get_available_versions(
                    target=attributes["target"],
                    source=attributes["source"],
                    exclude_pre_release=exclude_prerelease
                )
            )
            allowed_versions = get_allowed_versions(
                available_versions,
                attributes["lower_constraint"],
                attributes["lower_constraint_operator"],
                attributes["upper_constraint"],
                attributes["upper_constraint_operator"],
            )
            if ignore_constraints:
                versions = available_versions
            else:
                versions = allowed_versions

            # Versions
            current_version = attributes["version"]
            latest_available_version = get_latest_version(available_versions)
            latest_allowed_version = get_latest_version(allowed_versions)

            status = get_status(current_version, latest_available_version, latest_allowed_version, no_color=no_color)

            if not target:
                table.append([attributes["target"], attributes["name"], current_version, latest_available_version, attributes["constraint"], latest_allowed_version, status])
            else:
                for resource in target:
                    resource_type = resource[0]
                    resource_name = resource[1]
                    if resource_type in attributes["target"] and resource_name == attributes["name"]:
                        table.append([attributes["target"], attributes["name"], current_version, latest_available_version, attributes["constraint"], latest_allowed_version, status])
                    else:
                        pass

    print('\n')
    print("This was a plan only.  No files were updated.")
    table = tabulate(table, headers=table_headers, tablefmt='pretty')
    print(table)
    print('\n')

@cli.command("apply")
@click.option("--target", nargs=2, multiple=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--no-color", is_flag=True)
@click.option("--auto-approve", is_flag=True)
@click.pass_obj
def apply(config, target, exclude_prerelease, ignore_constraints, no_color, auto_approve):
    """
    Applies configuration version changes.
    """
    table_headers = ["resource\ntype", "module\nname", "current\nversion", "latest\navailable", "constraint", "latest\nallowed", "status"]
    table = []
    patterns = {
        "terraform": [r'(((terraform)) *{[^}]*?required_version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?)'],
        "providers": [r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'],
        "modules": [
            r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
            r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\?ref=([a-zA-Z]*\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})'
        ]
    }
    dependencies = get_dependencies(
        terraform_files=config["terraform_files"],
        patterns = patterns
    )
    if click.confirm("You are about to make changes to your configrations versions.  Would you like to proceed?"):
        for resource_type, resource in dependencies.items():
            for name, attributes in resource.items():
                available_versions = sort_versions(
                    get_available_versions(
                        target=attributes["target"],
                        source=attributes["source"],
                        exclude_pre_release=exclude_prerelease
                    )
                )
                allowed_versions = get_allowed_versions(
                    available_versions,
                    attributes["lower_constraint"],
                    attributes["lower_constraint_operator"],
                    attributes["upper_constraint"],
                    attributes["upper_constraint_operator"],
                )
                if ignore_constraints:
                    versions = available_versions
                else:
                    versions = allowed_versions

                # Versions
                current_version = attributes["version"]
                latest_available_version = get_latest_version(available_versions)
                latest_allowed_version = get_latest_version(allowed_versions)

                status = get_status(current_version, latest_available_version, latest_allowed_version, no_color=no_color)
                
                if not target:
                    if compare_versions(get_semantic_version(current_version), "!=", get_semantic_version(latest_allowed_version)):
                        update_version(
                            filepath=attributes["filepath"],
                            code=attributes["code"],
                            attribute="version",
                            value=latest_allowed_version
                        )
                        
                    table.append([attributes["target"], attributes["name"], current_version, latest_available_version, attributes["constraint"], latest_allowed_version, status])
                else:
                    for resource in target:
                        resource_type = resource[0]
                        resource_name = resource[1]
                        if resource_type in attributes["target"] and resource_name == attributes["name"]:
                            if compare_versions(get_semantic_version(current_version), "!=", get_semantic_version(latest_allowed_version)):
                                update_version(
                                    filepath=attributes["filepath"],
                                    code=attributes["code"],
                                    attribute="version",
                                    value=latest_allowed_version
                                )
                    
                            table.append([attributes["target"], attributes["name"], current_version, latest_available_version, attributes["constraint"], latest_allowed_version, status])
                        else:
                            pass

        print('\n')
        print("Configuration version were upgraded!")
        table = tabulate(table, headers=table_headers, tablefmt='pretty')
        print(table)
        print('\n')
    else:
        print("No changes were made.")

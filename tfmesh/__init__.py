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
@click.option("--top", type=int, default=5)
@click.pass_obj
def terraform(config, attribute, allowed, exclude_prerelease, top):
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
    print(result)

@get.command("providers")
@click.pass_obj
def providers(config):
    resources = get_resources(
        terraform_files=config["terraform_files"],
        patterns={
            "providers": [patterns("PROVIDER")],
        }
    )
    print(resources)

@get.command("provider")
@click.argument("name", type=str)
@click.argument("attribute", type=click.Choice(["target", "filepath", "filename", "code", "name", "source", "version", "versions", "constraint", "lower_constraint_operator", "lower_constraint", "upper_constraint_operator", "upper_constraint"]))
@click.option("--allowed", is_flag=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--top", type=int, default=5)
@click.pass_obj
def provider(config, name, attribute, allowed, exclude_prerelease, top):
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
    print(result)

@get.command("modules")
@click.pass_obj
def modules(config):
    resources = get_resources(
        terraform_files=config["terraform_files"],
        patterns={
            "modules": [
                patterns("MODULE_REGISTRY"),
                patterns("MODULE_GITHUB"),
            ],
        }
    )
    print(resources)

@get.command("module")
@click.argument("name", type=str)
@click.argument("attribute", type=click.Choice(["target", "filepath", "filename", "code", "name", "source", "version", "versions", "constraint", "lower_constraint_operator", "lower_constraint", "upper_constraint_operator", "upper_constraint"]))
@click.option("--allowed", is_flag=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--top", type=int, default=5)
@click.pass_obj
def module(config, name, attribute, allowed, exclude_prerelease, top):
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
    print(result)

@set.command("terraform")
@click.argument("attribute", type=click.Choice(["version", "constraint"]))
@click.argument("value")
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--what-if", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--force", is_flag=True)
@click.pass_obj
def terraform(config, attribute, value, exclude_prerelease, what_if, ignore_constraints, force):
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
    print(result)

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
    print(result)

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
    print(result)

@cli.command("plan")
@click.option("--target", nargs=2, multiple=True)
@click.option("--exclude-prerelease", is_flag=True)
@click.option("--ignore-constraints", is_flag=True)
@click.option("--no-color", is_flag=True)
@click.pass_obj
def plan(config, target, exclude_prerelease, ignore_constraints, no_color):
    table_headers = ["resource\ntype", "module\nname", "current\nversion", "latest\navailable", "constraint", "latest\nallowed", "status"]
    table = []
    dependencies = get_dependency_attributes(
        terraform_files=config["terraform_files"],
        patterns = {
            "terraform": [patterns("TERRAFORM")],
            "providers": [patterns("PROVIDER")],
            "modules": [
                patterns("MODULE_REGISTRY"),
                patterns("MODULE_GITHUB")
            ]
        }
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
    table_headers = ["resource\ntype", "module\nname", "current\nversion", "latest\navailable", "constraint", "latest\nallowed", "status"]
    table = []
    dependencies = get_dependency_attributes(
        terraform_files=config["terraform_files"],
        patterns = {
            "terraform": [patterns("TERRAFORM")],
            "providers": [patterns("PROVIDER")],
            "modules": [
                patterns("MODULE_REGISTRY"),
                patterns("MODULE_GITHUB")
            ]
        }
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

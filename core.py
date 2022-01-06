from pathlib import Path
import os
import requests
import json
import re
import operator
from tabulate import tabulate

def color(color="end"):
    colors = {
        "header": "\033[95m",
        "ok_blue": "\033[94m",
        "ok_cyan": "\033[96m",
        "ok_green": "\033[92m",
        "warning": "\033[93m",
        "fail": "\033[91m",
        "end": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
    }

    return colors[color]

def get_terraform_files(terraform_folder=None, file_pattern='*.tf'):
    """
    Get a list of absolute paths to terraform files matching the given pattern.
    """
    if terraform_folder:
        path = Path(terraform_folder)
    else:
        path = Path(os.getcwd())

    file_list = [str(x) for x in path.glob(file_pattern) if x.is_file()]
    
    return file_list

def get_semantic_version(version):
    """
    Get a dictionary of the semantic version components including major, minor, patch, and pre-release.
    """
    regex_pattern = r'((0|[1-9]\d*)\.*(0|[1-9]\d*)*\.*(0|[1-9]\d*)*(?:-(?:((?:[a-zA-Z]*(\d*)))))?)'

    try:
        version = re.findall(regex_pattern, version)[0]
        component_list = [int(component) for component in [version[1], version[2], version[3], version[5]] if component != '']
        version = tuple(component_list)
    except:
        version = None

    return version

def get_github_module_versions(user, repo, token=None):
    """
    Get tags from GitHub repo.
    """
    if token:
        headers = {'Authorization': 'token ' + token}
        response = requests.get(f"https://api.github.com/repos/{user}/{repo}/tags", headers=headers)
    else:
        response = requests.get(f"https://api.github.com/repos/{user}/{repo}/tags")

    tag_data = json.loads(response.text)

    tag_list = [x["name"] for x in tag_data]

    return tag_list

def get_terraform_module_versions(source):
    """
    Gets a list of versions for a given terraform module.
    """
    response = requests.get(f"https://registry.terraform.io/v1/modules/{source}")
    data = json.loads(response.text)
    
    return data["versions"]

def get_terraform_provider_versions(source):
    """
    Gets a list of versions for a given terraform provider such as aws, gcp, or azurerm.
    """
    response = requests.get(f"https://registry.terraform.io/v1/providers/{source}")
    data = json.loads(response.text)
    
    return data["versions"]

def get_terraform_versions():
    """
    Gets a list of terraform versions.
    """
    response = requests.get("https://releases.hashicorp.com/terraform")
    
    pattern = r'terraform_((\d+)\.*(\d+)*\.*(\d+)*-?([\S]*))</a>'
    versions = re.findall(pattern, response.text)

    return [version[0] for version in versions]

def get_dependencies(terraform_files):
    """
    Gets a list of dependencies that match a semantic version pattern.
    """
    terraform = r'(((terraform)) *{[^}]*?required_version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'
    terraform_providers = r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'
    terraform_modules = r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})'
    git_modules = r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\?ref=([a-zA-Z]*\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})'
    
    patterns = [
        terraform,
        terraform_providers,
        terraform_modules,
        git_modules,
    ]

    dependencies = []

    for terraform_file in terraform_files:
        with open(terraform_file) as f:
            path = Path(terraform_file)
            contents = f.read()

            for pattern in patterns:
                results = re.findall(pattern, contents, re.MULTILINE)

                if pattern == terraform:
                    target = "terraform"
                elif pattern == terraform_providers:
                    target = "provider"
                elif pattern == terraform_modules:
                    target = "module (registry)"
                elif pattern == git_modules:
                    target = "module (git)"

                for result in results:
                    data = {
                        "target": target,
                        "file_path": str(path),
                        "file_name:": path.name,
                        "code": result[0],
                        "name": result[1],
                        "source": result[2],
                        "version": result[3],
                        "constraint": result[4],
                        "lower_constraint_operator": result[5],
                        "lower_constraint": result[6],
                        "upper_constraint_operator": result[7],
                        "upper_constraint": result[8]
                    }
                    dependencies.append(data)
    
    return dependencies

def get_github_user_and_repo(source):
    """
    Returns a user and repo based on source.
    """
    pattern = r'github\.com[/:](.*?)/(.*?)(?:\.git|$)'
    result = re.findall(pattern, source, re.MULTILINE)[0]
    data = {
        "user": result[0],
        "repo": result[1]
    }

    return data

def get_available_versions(target, source):
    """
    Gets a list of available versions based on API calls to various endpoints.
    """
    # Get required environment variables
    github_token = os.environ["PAT_TOKEN"]

    # Pull available versions
    if target == "module (git)":
        data = get_github_user_and_repo(source)
        available_versions = get_github_module_versions(data["user"], data["repo"], token=github_token)
    elif target == "module (registry)":
        available_versions = get_terraform_module_versions(source)
    elif target == "provider":
        available_versions = get_terraform_provider_versions(source)
    elif target == "terraform":
        available_versions = get_terraform_versions()
    else:
        available_versions = None

    return available_versions

def get_allowed_versions(available_versions, lower_constraint="", lower_constraint_operator="", upper_constraint="", upper_constraint_operator=""):
    """
    Takes a list of available versions and considers constraints to get a list of allowed versions.
    """
    if lower_constraint and not lower_constraint_operator:
        lower_constraint_operator = "="

    if lower_constraint and lower_constraint_operator and upper_constraint and upper_constraint_operator:
        allowed_versions = [version for version in available_versions if compare_versions(get_semantic_version(version), lower_constraint_operator, get_semantic_version(lower_constraint)) and compare_versions(get_semantic_version(version), upper_constraint_operator, get_semantic_version(upper_constraint))]
    elif lower_constraint and lower_constraint_operator:
        allowed_versions = [version for version in available_versions if compare_versions(get_semantic_version(version), lower_constraint_operator, get_semantic_version(lower_constraint))]
    else:
        # Ensures that pre-release versions are removed if there are no constraints.
        allowed_versions = [version for version in available_versions if get_semantic_version(version)]

    # Add logic that applies global filters

    return allowed_versions

    # Apply logic to select the correct bump

def compare_versions(a, op, b):
    """
    Takes two tuples and compares them based on valid operations.
    """
    ops = {
        "<": operator.lt,
        "<=": operator.le,
        "=": operator.eq,
        "": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        ">": operator.gt,
    }

    if a and b:
        if op == "~>":
            if len(b) == 2:
                result = ops[">="](a, b) and ops["<"](a, (b[0]+1, 0, 0))
            elif len(b) == 3:
                result = ops[">="](a, b) and ops["<"](a, (b[0], b[1]+1, 0))
            else:
                raise ValueError("When using a pessimistic version constraint, the version value must only have two or three parts (e.g. 1.0, 1.1.0).")
        else:
            result = ops[op](a, b)
    else:
        result = False

    return result

def tuple_math(a, op, b):
    """
    Allows basic tuple math.
    """
    ops = {
        '+' : operator.add,
        '-' : operator.sub,
        '*' : operator.mul,
        '/' : operator.truediv,  # use operator.div for Python 2
        '%' : operator.mod,
        '^' : operator.xor,
    }

    result = tuple(map(ops[op], a, b))

    return result

def sort_versions(versions):
    """
    Sorts lists of versions based on the semantic version.  Normal sort does not work because of versions like 1.67.0 vs. 1.9.0.
    """
    tuple_versions = [get_semantic_version(version) for version in versions]
    versions = [x for _, x in sorted(zip(tuple_versions, versions), reverse=True)]

    return versions


def get_latest_version(versions):
    """
    Provides the latest version based on a list of provided versions.
    """
    if versions:
        versions = sort_versions(versions)
        latest_version = versions[0]
    else:
        latest_version = None

    return latest_version

def update_version(file_path, code, current_tag, latest_tag):
    """
    Reads existing terraform files, updates versions, and saves back.
    """
    # Read in the file
    with open(file_path, 'r') as f:
        data = f.read()

    # Replace the target string
    new_code = code.replace(current_tag, latest_tag)
    data = data.replace(code, new_code)

    # Write the file out again
    with open(file_path, 'w') as f:
        f.write(data)

def get_status(current_version, latest_available_version, latest_allowed_version):
    """
    Takes version details and outputs the status as a string.
    """
    current_version = get_semantic_version(current_version)
    latest_available_version = get_semantic_version(latest_available_version)
    latest_allowed_version = get_semantic_version(latest_allowed_version)

    if latest_allowed_version == None:
        status = f"{color('fail')}(x) no suitable version{color()}"
    elif compare_versions(current_version, "=", latest_available_version) and compare_versions(current_version, "=", latest_allowed_version):
        status = f"{color('ok_green')}(*) up-to-date{color()}"
    elif compare_versions(current_version, "!=", latest_available_version) and compare_versions(current_version, "=", latest_allowed_version):
        status = f"{color('warning')}(.) version pinned{color()}"
    elif compare_versions(current_version, "<", latest_available_version) and compare_versions(latest_available_version, "=", latest_allowed_version):
        status = f"{color('ok_green')}(->) upgraded to latest{color()}"
    elif compare_versions(current_version, "<", latest_available_version) and compare_versions(latest_available_version, ">", latest_allowed_version):
        status = f"{color('warning')}(>) upgraded to allowed{color()}"
    elif compare_versions(current_version, ">", latest_available_version) and compare_versions(latest_available_version, "=", latest_allowed_version):
        status = f"{color('ok_green')}(<-) downgraded to latest{color()}"
    elif compare_versions(current_version, ">", latest_allowed_version) and compare_versions(latest_available_version, ">", latest_allowed_version):
        status = f"{color('warning')}(<) downgraded to allowed{color()}"
    else:
        status = f"{color('fail')}(!) you found a bug{color()}"

    return status
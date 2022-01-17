from pathlib import Path
import os
import requests
import json
import re
import operator
import yaml
from tabulate import tabulate
from collections import defaultdict

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
        path = Path(terraform_folder).absolute()
    else:
        path = Path(os.getcwd())

    file_list = [str(x) for x in path.glob(file_pattern) if x.is_file()]
    
    return file_list

def set_config(config_file=".tfmesh.yaml", terraform_folder="", terraform_file_pattern="*.tf"):
    with open(config_file, 'w') as config_file:
        config = {
            "terraform_folder": terraform_folder,
            "terraform_file_pattern": terraform_file_pattern,
            "terraform_files": get_terraform_files(terraform_folder, terraform_file_pattern)
        }
        yaml.dump(config, config_file, default_flow_style=False)

def get_config(config_file=".tfmesh.yaml"):
    return yaml.safe_load(open(config_file))

def get_dependencies(terraform_files, patterns):
    """
    """
    dependencies = defaultdict(dict)

    for terraform_file in terraform_files:
        contents = open(terraform_file).read()

        for target, pattern_list in patterns.items():
            for pattern in pattern_list:
                results = re.findall(pattern, contents, re.MULTILINE)
                
                for result in results:
                    if result != []:
                        dependency = {
                            "target": target,
                            "filepath": terraform_file, 
                            "filename": Path(terraform_file).name,
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

                        dependencies[target][result[1]] = dependency

    return dependencies

def get_semantic_version(version):
    """
    Get a dictionary of the semantic version components including major, minor, patch, and pre-release.
    """
    regex_pattern = r'(\d+)\.*(\d+)*\.*(\d+)*(?:-*(?:(?:[a-zA-Z]*(\d*)))?)'

    try:
        version = re.findall(regex_pattern, version)[0]
        version = tuple([int(component) for component in version if component != ''])
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

def get_available_versions(target, source=None, exclude_pre_release=False):
    """
    Gets a list of available versions based on API calls to various endpoints.
    """
    # Get required environment variables
    github_token = os.environ["PAT_TOKEN"]

    # Pull available versions
    if target == "modules" and "github" in source:
        data = get_github_user_and_repo(source)
        available_versions = get_github_module_versions(data["user"], data["repo"], token=github_token)
    elif target == "modules":
        available_versions = get_terraform_module_versions(source)
    elif target == "providers":
        available_versions = get_terraform_provider_versions(source)
    elif target == "terraform":
        available_versions = get_terraform_versions()
    else:
        available_versions = None

    if exclude_pre_release:
        available_versions = [version for version in available_versions if len(get_semantic_version(version)) < 4]

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

    return allowed_versions

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
        '/' : operator.truediv,
        '%' : operator.mod,
        '^' : operator.xor,
    }

    result = tuple(map(ops[op], a, b))

    return result

def sort_versions(versions, reverse=True):
    """
    Sorts lists of versions based on the semantic version.  Normal sort does not work because of versions like 1.67.0 vs. 1.9.0.
    """
    tuple_versions = [get_semantic_version(version) for version in versions]
    versions = [x for _, x in sorted(zip(tuple_versions, versions), reverse=reverse)]

    return versions

def print_list(versions, top=None):
    """
    """
    if top:
        versions = versions[:top]

    for version in versions:
        print(f'- {version}')

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

def update_version(filepath, code, attribute, value):
    """
    Reads existing terraform files, updates versions, and saves back.
    """
    #TODO: Rename this function
    patterns = {
        "version": r'(= *"*)([a-zA-Z]*[\S]+)(\" *#? *[=!><~(.*)]* *[0-9\.]+ *,* *[=!><~(.*)]* *[0-9\.]+)',
        "constraint": r'(= *"*[a-zA-Z]*[\S]+\" *#? *)([=!><~(.*)]* *[0-9\.]+ *,* *[=!><~(.*)]* *[0-9\.]+)*()',
    }

    # Handle edge case where constraint is added to resource with no current constraint
    if attribute == "constraint":
        result = re.findall(patterns[attribute], code)
        current_constraint = result[0][1]
        if current_constraint == "" and "#" not in value:
            value = f' # {value}'

    # Read in the file
    with open(filepath, 'r') as f:
        data = f.read()

    # Replace the target string
    new_code = re.sub(patterns[attribute], r'\1__value__\3', code)
    new_code = new_code.replace("__value__", value)

    data = data.replace(code, new_code)

    # Write the file out again
    with open(filepath, 'w') as f:
        f.write(data)

def get_status(current_version, latest_available_version, latest_allowed_version, no_color=False):
    """
    Takes version details and outputs the status as a string.
    """
    current_version = get_semantic_version(current_version)
    latest_available_version = get_semantic_version(latest_available_version)
    latest_allowed_version = get_semantic_version(latest_allowed_version)

    if latest_allowed_version == None:
        status = f"{'' if no_color else color('fail')}(x) no suitable version{'' if no_color else color()}"
    elif compare_versions(current_version, "=", latest_available_version) and compare_versions(current_version, "=", latest_allowed_version):
        status = f"{'' if no_color else color('ok_green')}(*) up-to-date{'' if no_color else color()}"
    elif compare_versions(current_version, "!=", latest_available_version) and compare_versions(current_version, "=", latest_allowed_version):
        status = f"{'' if no_color else color('warning')}(.) pinned out-of-date{'' if no_color else color()}"
    elif compare_versions(current_version, "<", latest_available_version) and compare_versions(latest_available_version, "=", latest_allowed_version):
        status = f"{'' if no_color else color('ok_green')}(->) upgraded to latest{'' if no_color else color()}"
    elif compare_versions(current_version, "<", latest_available_version) and compare_versions(latest_available_version, ">", latest_allowed_version):
        status = f"{'' if no_color else color('warning')}(>) upgraded to allowed{'' if no_color else color()}"
    elif compare_versions(current_version, ">", latest_available_version) and compare_versions(latest_available_version, "=", latest_allowed_version):
        status = f"{'' if no_color else color('ok_green')}(<-) downgraded to latest{'' if no_color else color()}"
    elif compare_versions(current_version, ">", latest_allowed_version) and compare_versions(latest_available_version, ">", latest_allowed_version):
        status = f"{'' if no_color else color('warning')}(<) downgraded to allowed{'' if no_color else color()}"
    else:
        status = f"{'' if no_color else color('fail')}(!) you found a bug{'' if no_color else color()}"

    return status
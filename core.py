from pathlib import Path
import os
import requests
import json
import re
import operator
from tabulate import tabulate

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
    regex_pattern = r'((\d+)\.*(\d+)*\.*(\d+)*[^a-zA-Z\d\s:]*(.*))'
    # regex_pattern = r"(\d*)\.(\d*)\.?(\d*)[^a-zA-Z\d\s:]?(.*)"
    # Get first match and first result
    version = re.findall(regex_pattern, version)[0][0]

    return version_tuple(version)

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

def get_terraform_module_versions(module_source):
    """
    Gets a list of versions for a given terraform module.
    """
    response = requests.get(f"https://registry.terraform.io/v1/modules/{module_source}")
    data = json.loads(response.text)
    
    return data["versions"]

def get_terraform_provider_versions(provider):
    """
    Gets a list of versions for a given terraform provider such as aws, gcp, or azurerm.
    """
    response = requests.get(f"https://registry.terraform.io/v1/providers/{provider}")
    data = json.loads(response.text)
    
    return data["versions"]

def get_modules(terraform_file_list):
    """
    Gets a list of modules that match a semantic version pattern.
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

    modules = []

    for terraform_file in terraform_file_list:
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
                        "lower_constraint": version_tuple(result[6]),
                        "upper_constraint_operator": result[7],
                        "upper_constraint": version_tuple(result[8])
                    }
                    modules.append(data)
    
    return modules

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

def get_valid_versions(module_source, module_version, lower_constraint, lower_constraint_operator, upper_constraint, upper_constraint_operator, global_bump_setting="minor"):
    """
    Takes in module version and constraint information to create a list of valid versions
    """
    # Pull available versions
    if module["target"] == "module (git)":
        data = get_github_user_and_repo(module_source)
        available_versions = get_github_module_versions(data["user"], data["repo"], token=github_token)
    elif module["target"] == "module (registry)":
        available_versions = get_terraform_module_versions(module_source)
    elif module["target"] == "provider":
        available_versions = get_terraform_provider_versions(module_source)
    elif module["target"] == "terraform":
        pass

    # Get latest major, minor, and patch versionsį
    # version_components = get_semantic_version(module_version)

    if lower_constraint and not lower_constraint_operator:
        lower_constraint_operator = "="

    if lower_constraint and lower_constraint_operator and upper_constraint and upper_constraint_operator:
        allowed_versions = [version for version in available_versions if compare_versions(get_semantic_version(version), lower_constraint_operator, lower_constraint) and compare_versions(get_semantic_version(version), upper_constraint_operator, upper_constraint)]
    elif lower_constraint and lower_constraint_operator:
        allowed_versions = [version for version in available_versions if compare_versions(get_semantic_version(version), lower_constraint_operator, lower_constraint)]
    else:
        allowed_versions = available_versions

    

    # Add logic that applies global filters

    allowed_versions.sort()

    # print(f'Module: {module["name"]}, Current Version: {current_version}')
    # print(f'Available versions: {available_versions}')
    # print(f'Allowed versions: {allowed_versions}')

    return allowed_versions

    # Apply logic to select the correct bump

def version_tuple(version):
    """
    Turns a semantic version value into a tuple used for version comparison operations.
    """
    try:
        version = tuple(map(int, (version.split("."))))
    except:
        version = None

    return version

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

def get_latest_version(version_list):
    """
    Provides the latest version based on a list of provided versions.
    """
    version_list.sort(reverse=True)
    latest_version = version_list[0]
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

github_token = os.environ["PAT_TOKEN"]
files = get_terraform_files("terraform")
modules = get_modules(files)

table_headers = ["target", "name", "current version", "constraint", "new version", "status"]
table = []

for module in modules:
    current_version = module["version"]
    valid_versions = get_valid_versions(
        module["source"], 
        module["version"], 
        module["lower_constraint"], 
        module["lower_constraint_operator"], 
        module["upper_constraint"], 
        module["upper_constraint_operator"]
    )
    latest_version = get_latest_version(valid_versions)

    if current_version != latest_version:
        update_version(module["file_path"], module["code"], current_version, latest_version)
        if compare_versions(get_semantic_version(current_version), ">", get_semantic_version(latest_version)):
            status = "downgraded"
        else:
            status = "upgraded"
    else:
        status = "up-to-date"
        latest_version = None
        
    table.append([module["target"], module["name"], current_version, module["constraint"], latest_version, status])

print(tabulate(table, headers=table_headers, tablefmt='orgtbl'))
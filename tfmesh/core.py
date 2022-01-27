from pathlib import Path
import os
import requests
import json
import re
import operator
import yaml
from tabulate import tabulate
from collections import defaultdict

def get_color(color="end"):
    """
    """
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

def patterns(pattern):
    """
    """
    patterns = {
        "TERRAFORM": r'(((terraform)) *{[^}]*?required_version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?)',
        "PROVIDER": r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})',
        "MODULE_REGISTRY": r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
        "MODULE_GITHUB": r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\?ref=([a-zA-Z]*\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
    }

    return patterns[pattern]

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

def set_config(config_file=".tfmesh.yaml", terraform_folder="", terraform_file_pattern="*.tf", var=[]):
    """
    """
    variables = {}
    for v in var:
        name, value = re.findall(r'(\S*) *= *(\S*)', v)[0]
        name = re.sub(r'[^a-zA-Z0-9_]', "", name)
        variables[name] = value

    with open(config_file, 'w') as config_file:
        config = {
            "terraform_folder": terraform_folder,
            "terraform_file_pattern": terraform_file_pattern,
            "terraform_files": get_terraform_files(terraform_folder, terraform_file_pattern),
            "variables": variables
        }
        yaml.dump(config, config_file, default_flow_style=False)

def get_config(config_file=".tfmesh.yaml"):
    try:
        config = yaml.safe_load(open(config_file))
    except:
        config = None
    return config

def get_dependency_attributes(terraform_files, patterns):
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

def get_dependency_attribute(terraform_files, patterns, resource_type, name, attribute, allowed, exclude_prerelease, top):
    """
    """
    dependencies = get_dependency_attributes(
        terraform_files=terraform_files,
        patterns=patterns
    )
    if attribute == "versions":
        request = get_available_versions(
            target=dependencies[resource_type][name]["target"],
            source=dependencies[resource_type][name]["source"],
            exclude_pre_release=exclude_prerelease
        )
        available_versions = sort_versions(request["versions"])
        allowed_versions = sort_versions(
            get_allowed_versions(
                available_versions,
                dependencies[resource_type][name]["lower_constraint"],
                dependencies[resource_type][name]["lower_constraint_operator"],
                dependencies[resource_type][name]["upper_constraint"],
                dependencies[resource_type][name]["upper_constraint_operator"],
            )
        )
        if request["status_code"] != 200:
            result = pretty_print(f'The API call to return versions for {name} failed. {request["status_code"]} {request["reason"]}.')
        elif allowed:
            result = pretty_print(allowed_versions, top=top)
        else:
            result = pretty_print(available_versions, top=top)
    else:
        if attribute == "code":
            result = pretty_print(pretty_code(dependencies[resource_type][name][attribute]))
        else:
            result = pretty_print(dependencies[resource_type][name][attribute])

    return result

def set_dependency_attribute(terraform_files, patterns, resource_type, name, attribute, value, exclude_prerelease, what_if, ignore_constraints, force):
    dependencies = get_dependency_attributes(
        terraform_files=terraform_files,
        patterns=patterns
    )
    if attribute == "version":
        request = get_available_versions(
            target=dependencies[resource_type][name]["target"],
            source=dependencies[resource_type][name]["source"],
            exclude_pre_release=exclude_prerelease
        )
        available_versions = sort_versions(request["versions"])
        allowed_versions = sort_versions(
            get_allowed_versions(
                available_versions,
                dependencies[resource_type][name]["lower_constraint"],
                dependencies[resource_type][name]["lower_constraint_operator"],
                dependencies[resource_type][name]["upper_constraint"],
                dependencies[resource_type][name]["upper_constraint_operator"],
            )
        )
        if ignore_constraints:
            versions = available_versions
        else:
            versions = allowed_versions
    else:
        versions = []

    current_value = dependencies[resource_type][name][attribute]
    new_value = value

    if current_value == new_value:
        result = pretty_print(f'The {attribute} is already set to "{new_value}".')
    elif what_if:
        result = pretty_print(f'The {attribute} was would have changed from "{current_value}" to "{new_value}".')
    elif attribute == "version" and request["status_code"] != 200 and force:
        update_version(
            filepath=dependencies[resource_type][name]["filepath"],
            code=dependencies[resource_type][name]["code"],
            attribute=attribute,
            value=value
        )
        result = pretty_print(f'The {attribute} was changed from "{current_value}" to "{new_value}" without validation.')
    elif attribute == "version" and request["status_code"] != 200:
        result = pretty_print(f'The API call to return versions for {name} failed.')
    elif force or new_value in versions or attribute == "constraint":
        update_version(
            filepath=dependencies[resource_type][name]["filepath"],
            code=dependencies[resource_type][name]["code"],
            attribute=attribute,
            value=value
        )
        result = pretty_print(f'The {attribute} was changed from "{current_value}" to "{new_value}".')
    elif versions == []:
        result = pretty_print(f'There is no version available that meets the constraint "{dependencies[resource_type][name]["constraint"]}".')
    else:
        title = f'"{value}" is not an acceptable version.  Select from one of:'
        result = pretty_print(versions, title=title)
    
    return result

def get_resources(terraform_files, patterns):
    """
    """
    resource_list = []

    dependencies = get_dependency_attributes(
        terraform_files=terraform_files,
        patterns=patterns
    )
    for resource_type, resources in dependencies.items():
        for resource in resources:
            resource_list.append(resource)

    return pretty_print(resource_list)

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

    if response.status_code == 200:
        tag_data = json.loads(response.text)
        versions = [x["name"] for x in tag_data]
    else:
        # error = f'{response.status_code} {response.reason}'
        versions = []

    result = {
        "status_code": response.status_code,
        "reason": response.reason,
        "versions": versions
    }

    return result

def get_terraform_module_versions(source):
    """
    Gets a list of versions for a given terraform module.
    """
    response = requests.get(f"https://registry.terraform.io/v1/modules/{source}")
    data = json.loads(response.text)

    result = {
        "status_code": response.status_code,
        "reason": response.reason,
        "versions": data["versions"]
    }
    
    return result

def get_terraform_provider_versions(source):
    """
    Gets a list of versions for a given terraform provider such as aws, gcp, or azurerm.
    """
    response = requests.get(f"https://registry.terraform.io/v1/providers/{source}")
    data = json.loads(response.text)

    result = {
        "status_code": response.status_code,
        "reason": response.reason,
        "versions": data["versions"]
    }
    
    return result

def get_terraform_versions():
    """
    Gets a list of terraform versions.
    """
    response = requests.get("https://releases.hashicorp.com/terraform")
    
    pattern = r'terraform_((\d+)\.*(\d+)*\.*(\d+)*-?([\S]*))</a>'
    versions = re.findall(pattern, response.text)

    result = {
        "status_code": response.status_code,
        "reason": response.reason,
        "versions": [version[0] for version in versions]
    }

    return result

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
    try:
        github_token = os.environ["TFMESH_GITHUB_TOKEN"]
    except:
        github_token = ""

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
        versions = available_versions["versions"]
        available_versions["versions"] = [version for version in versions if len(get_semantic_version(version)) < 4]

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

def pretty_print(ugly_list, title=None, top=None, item_prefix=" - "):
    """
    """
    pretty_print = "\n"

    if isinstance(ugly_list, str):
        ugly_list = [ugly_list]

    if len(ugly_list) > 1:
        item_prefix = item_prefix
    else:
        item_prefix = ""

    if title:
        pretty_print += f'{title}\n'

    if top:
        ugly_list = ugly_list[:top]

    for ugly_item in ugly_list:
        pretty_print += f'{item_prefix}{ugly_item}\n'

    return pretty_print

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
        "version": r'(=|")([a-zA-Z]?[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+)?)(")',
        "constraint": r'(" *#+ *)([=!><~(.*)]* *[0-9\.]+ *,* *[=!><~(.*)]* *[0-9\.]+)*()',
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

def get_status(current_version, latest_available_version, latest_allowed_version):
    """
    Takes version details and outputs the status as a string.

    ~ no change
    + upgraded
    - downgraded

    * latest available
    . latest allowed
    x no suitable version
    ! bug
    """
    current_version = get_semantic_version(current_version)
    latest_available_version = get_semantic_version(latest_available_version)
    latest_allowed_version = get_semantic_version(latest_allowed_version)

    if latest_allowed_version == None:
        status = {
            "symbol": "~/x",
            "action": "no change",
            "status": "no suitable version",
            "color": "fail"
        }
    elif compare_versions(current_version, "=", latest_available_version) and compare_versions(current_version, "=", latest_allowed_version):
        status = {
            "symbol": "~/*",
            "action": "no change",
            "status": "latest available",
            "color": "ok_green"
        }
    elif compare_versions(current_version, "!=", latest_available_version) and compare_versions(current_version, "=", latest_allowed_version):
        status = {
            "symbol": "~/.",
            "action": "no change",
            "status": "latest allowed",
            "color": "warning"
        }
    # current < available and available = allowed
    elif compare_versions(current_version, "<", latest_available_version) and compare_versions(latest_available_version, "=", latest_allowed_version):
        status = {
            "symbol": "+/*",
            "action": "upgrade",
            "status": "latest available",
            "color": "ok_green"
        }
    # current < available and current < allowed
    elif compare_versions(current_version, "<", latest_available_version) and compare_versions(current_version, "<", latest_allowed_version):
        status = {
            "symbol": "+/.",
            "action": "upgrade",
            "status": "latest allowed",
            "color": "warning"
        }
    # current > available and available = allowed
    elif compare_versions(current_version, ">", latest_available_version) and compare_versions(latest_available_version, "=", latest_allowed_version):
        status = {
            "symbol": "-/*",
            "action": "downgrade",
            "status": "latest available",
            "color": "warning"
        }
    # current < available and current > allowed
    elif compare_versions(current_version, ">=", latest_available_version) and compare_versions(current_version, ">", latest_allowed_version):
        status = {
            "symbol": "-/.",
            "action": "downgrade",
            "status": "latest allowed",
            "color": "warning"
        }
    # current > available and current > allowed
    elif compare_versions(current_version, ">", latest_available_version) and compare_versions(current_version, ">", latest_allowed_version):
        status = {
            "symbol": "-/.",
            "action": "downgrade",
            "status": "latest allowed",
            "color": "warning"
        }
    else:
        status = {
            "symbol": "~/!",
            "action": "no change",
            "status": "bug",
            "color": "fail"
        }

    return status

def prefix_status(status, string, color=None, no_color=False):
    index = 0
    for char in string:
        if re.match(r'[\S]', char):
            break
        else:
            index += 1

    status_length = len(status) + 1

    if index < status_length:
        string = " " * (status_length - index) + string
        index = status_length

    position = index - 2
    line = f'{string[:position]}{"" if no_color else get_color(color)}{status}{"" if no_color else get_color()}{string[position+1:]}'
    line = line[len(status) - 1:]

    return line

def run_plan_apply(terraform_files, patterns, target=[], apply=False, verbose=False, exclude_prerelease=False, ignore_constraints=False, no_color=False):
    """
    
    """
    # get resource attributes
    resources = get_dependency_attributes(terraform_files, patterns)

    # limit resources to targets if there are targets
    if target:
        tmp_resources = defaultdict(dict)
        for resource in target:
            print(f'resource: {resource}')
            resource_type = resource[0]
            resource_name = resource[1]

            tmp_resources[resource_type][resource_name] = resources[resource_type][resource_name]
        resources = tmp_resources
    else:
        pass

    # print the header text
    print(f'{"" if no_color else get_color("ok_green")}')
    print("Resource actions and version statuses are indicated with the following symbols:")
    print('\n')
    print("Actions:")
    print("+: upgraded")
    print("-: downgraded")
    print("~: no change")
    print('\n')
    print("Version status:")
    print("*: latest available version")
    print(".: latest allowed version based on constraints")
    print("x: no suitable version")
    print("!: bug")
    print('\n')
    print("Actions and and versions are used together separated by a forward slash (/) to indicate changes.")
    print("For example, '+/*' would indicate the version will be upgraded to the latest version")
    print('\n')
    print("Terraform Mesh will perform the following actions:")
    print(f'{"" if no_color else get_color()}')

    # create map for tracking changes
    plan = {
        "upgrade": 0,
        "downgrade": 0,
        "no change": 0
    }

    failures = 0

    # iterate through resources to get available and allowed versions
    for resource_type, resources in resources.items():
        for resource, attributes in resources.items():
            request = get_available_versions(
                target=attributes["target"],
                source=attributes["source"],
                exclude_pre_release=exclude_prerelease
            )
            available_versions = request["versions"]
            allowed_versions = get_allowed_versions(
                available_versions,
                attributes["lower_constraint"],
                attributes["lower_constraint_operator"],
                attributes["upper_constraint"],
                attributes["upper_constraint_operator"],
            )

            # get the latest versions
            current_version = attributes["version"]
            latest_available_version = get_latest_version(available_versions)
            if ignore_constraints:
                latest_allowed_version = latest_available_version
            else:
                latest_allowed_version = get_latest_version(allowed_versions)

            # get the status
            status = get_status(current_version, latest_available_version, latest_allowed_version)

            code = pretty_code(attributes["code"])

            # split code on newlines so it can be output line by line
            code = code.split('\n')

            # do some stuff is the current version is not the same as the allowed version
            if compare_versions(get_semantic_version(current_version), "!=", get_semantic_version(latest_allowed_version)):
                plan[status["action"]] += 1

                # iterate through code
                for line in code:
                    if current_version in line:
                        print(f'{prefix_status(status["symbol"], line, status["color"], no_color)}{"" if no_color else get_color(status["color"])} // {status["action"]}{"d" if apply else ""} to {status["status"]} = {latest_allowed_version}{"" if no_color else get_color()}')
                    else:
                        print(line)

                print("\n")
                # print("...")
                # print("\n")

                if apply:
                    update_version(
                        filepath=attributes["filepath"],
                        code=attributes["code"],
                        attribute="version",
                        value=latest_allowed_version
                    )
                else:
                    pass
            else:
                if request["status_code"] != 200:
                    failures += 1
                if verbose:
                    plan["no change"] += 1
                    if request["status_code"] != 200:
                        print(f'{get_color("fail")}~/x {get_color()}The API call to return versions for {attributes["target"]} "{attributes["name"]}" failed.{get_color("fail")} // {request["status_code"]} {request["reason"]}.{get_color()}\n\n')
                    else:
                        # iterate through code
                        for line in code:
                            if current_version in line:
                                print(f'{prefix_status(status["symbol"], line, status["color"])}{"" if no_color else get_color(status["color"])} // {status["action"]} - {status["status"]}{"" if no_color else get_color()}')
                            else:
                                print(line)

                        print("\n")

    if apply:
        print(f'{"" if no_color else get_color("ok_green")}Apply complete!  Resources: {plan["upgrade"]} upgraded, {plan["downgrade"]} downgraded{"" if no_color else get_color()}')
    elif plan["no change"] > 0:
        print(f'{"" if no_color else get_color("ok_green")}Plan: {plan["upgrade"]} to upgrade (+), {plan["downgrade"]} to downgrade (-), {plan["no change"]} not to change (~){"" if no_color else get_color()}')
    elif plan["upgrade"] > 0 or plan["downgrade"] > 0:
        print(f'{"" if no_color else get_color("ok_green")}Plan: {plan["upgrade"]} to upgrade, {plan["downgrade"]} to downgrade{"" if no_color else get_color()}')
    else:
        print(f'{"" if no_color else get_color("ok_green")}No changes.  Dependency versions are up-to-date.{"" if no_color else get_color()}')

    if failures >= 1:
        print(f'\n{"" if no_color else get_color("fail")}Warning: {failures} resource(s) failed to return a list of available versions.{"" if no_color else get_color()}')
        if apply:
            print(f'{"" if no_color else get_color("fail")}These resources were not modified during apply.{"" if no_color else get_color()}')
        if not verbose:
            print(f'{"" if no_color else get_color("fail")}For more details, run the command again with the "--verbose" flag.{"" if no_color else get_color()}')

    return None

def pretty_code(code, spaces=4, indent_symbols = ("{", "[", "("), outdent_symbols = ("}", "]", ")")):
    """
    Return nicely formated nested code.
    """
    # initialize variables
    indent = 0
    new_code = []

    # get each line of code separately
    code = code.split('\n')

    # loop through each line of code
    for line in code:

        # keep track of the last indent for a comparision to the current indent later
        last_indent = indent
        
        # add indents based on indent_symbols
        for symbol in indent_symbols:
            indent += line.count(symbol)*spaces

        # remove indents based on outdent_symbols
        for symbol in outdent_symbols:
            indent -= line.count(symbol)*spaces

        # compare the current indent to the last indent
        # and determine the appropriate indent level
        if indent > last_indent:
            current_indent = last_indent
        else:
            current_indent = indent

        # use regex to create the newly formatted line
        pattern = r'^ +(.*)'
        line_of_code = re.sub(pattern, fr'{" "*current_indent}\1', line)

        new_code.append(line_of_code)

    return "\n".join(new_code)

def set_environment_variables(var, config_file=".tfmesh.yaml"):
    """
    Sets environment variables based on config and command line variables.
    """
    # load configuration file variables
    try:
        config_variables = yaml.safe_load(open(config_file))["variables"]
    except:
        config_variables = {}

    # collect and clean command line variables
    command_line_variables = {}
    for v in var:
        name, value = re.findall(r'(\S*) *= *(\S*)', v)[0]
        name = name.replace("-", "_")
        name = re.sub(r'[^a-zA-Z0-9_]', "", name)
        command_line_variables[name] = value

    # merge config variables with command line variables
    variables = dict(list(config_variables.items()) + list(command_line_variables.items()))

    # set environment variables
    for name, value in variables.items():
        # set the environment variable
        name = f"TFMESH_{name.upper()}"
        os.environ[name] = value

    return variables
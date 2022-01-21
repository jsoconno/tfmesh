from tfmesh.core import *

terraform_files = get_terraform_files("terraform")

def run_plan_apply(terraform_files, patterns, apply=False):
    """
    
    """
    # get resource attributes
    resources = get_dependency_attributes(terraform_files, patterns)

    # print the header text
    print(get_color('ok_green'))
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
    print(get_color())

    # create map for tracking changes
    plan = {
        "upgrade": 0,
        "downgrade": 0,
        "no change": 0
    }

    # iterate through resources to get available and allowed versions
    for resource_type, resources in resources.items():
        for resource, attributes in resources.items():
            available_versions = get_available_versions(attributes["target"], attributes["source"])
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
            latest_allowed_version = get_latest_version(allowed_versions)

            # get the status
            status = get_status(current_version, latest_available_version, latest_allowed_version)

            # account for lost spaces in regex for providers (need more dynamic fix)
            if attributes["target"] == "providers":
                code = "        " + attributes["code"]
            else:
                code = attributes["code"]

            # split code on newlines so it can be output line by line
            code = code.split('\n')

            # do some stuff is the current version is not the same as the allowed version
            if compare_versions(get_semantic_version(current_version), "!=", get_semantic_version(latest_allowed_version)):
                plan[status["action"]] += 1

                # iterate through code
                for line in code:
                    if current_version in line:
                        print(f'{prefix_status(status["symbol"], line, status["color"])}{get_color(status["color"])} // {status["action"]} to {status["status"]} = {latest_allowed_version}{get_color()}')
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

    if apply:
        print(f'{get_color("ok_green")}Apply complete!  Resources: {plan["upgrade"]} upgraded, {plan["downgrade"]} downgraded{get_color()}')
    # elif plan["no change"] > 0:
    #     print(f'{get_color("ok_green")}Plan: {plan["upgrade"]} to upgrade (+), {plan["downgrade"]} to downgrade (-), {plan["no change"]} not to change (~){get_color()}')
    elif plan["upgrade"] > 0 or plan["downgrade"] > 0:
        print(f'{get_color("ok_green")}Plan: {plan["upgrade"]} to upgrade, {plan["downgrade"]} to downgrade{get_color()}')
    else:
        print(f'{get_color("ok_green")}No changes.  Dependency versions are up-to-date.{get_color()}')

    return None
    

run_plan_apply(
    terraform_files=terraform_files,
    patterns = {
        "terraform": [r'(((terraform)) *{[^}]*?required_version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?)'],
        "providers": [r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'],
        "modules": [
            r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
            r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\?ref=([a-zA-Z]*\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})'
        ]
    },
    apply=True
)


#         if compare_versions(get_semantic_version(current_version), "!=", get_semantic_version(latest_allowed_version)):
#             if compare_versions(get_semantic_version(current_version), ">", get_semantic_version(latest_allowed_version)):
#                 plan["downgrade"] += 1
#             elif compare_versions(get_semantic_version(current_version), "<", get_semantic_version(latest_allowed_version)):
#                 plan["upgrade"] += 1
#             else:
#                 pass

#             for line in code:
#                 if current_version in line:
#                     print(prefix_status(status["symbol"], line, status["color"]), "//", status["action"], status["status"], "=", latest_allowed_version)
#                 else:
#                     print(line)

#             print("\n")
#             # print("...")
#             # print("\n")
#         else:
#             if verbose:
#                 plan["no change"] += 1

#                 for line in code:
#                     if current_version in line:
#                         print(prefix_status(status["symbol"], line, status["color"]), "//", status["action"], status["status"], "=", latest_allowed_version)
#                     else:
#                         print(line)

#                 print("\n")
#                 # print("...")
#                 # print("\n")

# if plan["no change"] > 0:
#     print(f'{get_color("ok_green")}Plan: {plan["upgrade"]} to upgrade (+), {plan["downgrade"]} to downgrade (-), {plan["no change"]} not to change (~){get_color()}')
# elif plan["upgrade"] > 0 or plan["downgrade"] > 0:
#     print(f'{get_color("ok_green")}Plan: {plan["upgrade"]} to upgrade, {plan["downgrade"]} to downgrade{get_color()}')
# else:
#     print(f'{get_color("ok_green")}No changes.  Dependency versions are up-to-date.{get_color()}')
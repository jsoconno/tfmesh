from core import *

files = get_terraform_files("terraform")
dependencies = get_dependencies(files)

table_headers = ["resource type", "name", "current version", "latest version", "constraint", "latest allowed version", "status"]
table = []

for dependency in dependencies:
    available_versions = get_available_versions(dependency["target"], dependency["source"])
    print(dependency["name"])
    print('-----------')
    print(dependency["lower_constraint"])
    print(dependency["lower_constraint_operator"])
    allowed_versions = get_allowed_versions(
        available_versions,
        dependency["lower_constraint"],
        dependency["lower_constraint_operator"],
        dependency["upper_constraint"],
        dependency["upper_constraint_operator"],
    )

    # Versions
    current_version = dependency["version"]
    latest_version = get_latest_version(available_versions)
    latest_allowed_version = get_latest_version(allowed_versions)

    if latest_allowed_version == None:
        status = f"{color('warning')}no suitable version{color()}"
    elif current_version != latest_allowed_version and dependency["constraint"] == "":
        status = f"{color('ok_blue')}pinned-outdated{color()}"
    elif current_version != latest_allowed_version:
        update_version(dependency["file_path"], dependency["code"], current_version, latest_allowed_version)
        if compare_versions(get_semantic_version(current_version), ">", get_semantic_version(latest_allowed_version)):
            status = f"{color('ok_cyan')}downgraded{color()}"
        else:
            status = f"{color('ok_green')}upgraded{color()}"
    else:
        status = f"up-to-date"
        
    table.append([dependency["target"], dependency["name"], current_version, latest_version, dependency["constraint"], latest_allowed_version, status])

print('\n')
print(tabulate(table, headers=table_headers, tablefmt='orgtbl'))
print('\n')
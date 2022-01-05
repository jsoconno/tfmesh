from core import *

files = get_terraform_files("terraform")
dependencies = get_dependencies(files)

table_headers = ["resource type", "name", "config version", "constraint", "latest version", "status"]
table = []

for dependency in dependencies:
    current_version = dependency["version"]
    valid_versions = get_valid_versions(
        dependency["target"],
        dependency["source"], 
        dependency["version"], 
        dependency["lower_constraint"], 
        dependency["lower_constraint_operator"], 
        dependency["upper_constraint"], 
        dependency["upper_constraint_operator"],
    )
    latest_version = get_latest_version(valid_versions)

    if current_version != latest_version and dependency["constraint"] == "":
        status = f"{color('ok_blue')}pinned-outdated{color()}"
    elif current_version != latest_version:
        update_version(dependency["file_path"], dependency["code"], current_version, latest_version)
        if compare_versions(get_semantic_version(current_version), ">", get_semantic_version(latest_version)):
            status = f"{color('ok_cyan')}downgraded{color()}"
        else:
            status = f"{color('ok_green')}upgraded{color()}"
    else:
        status = f"up-to-date"
        latest_version = None
        
    table.append([dependency["target"], dependency["name"], current_version, dependency["constraint"], latest_version, status])

print('\n')
print(tabulate(table, headers=table_headers, tablefmt='orgtbl'))
print('\n')
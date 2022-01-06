from core import *

dry_run = False

files = get_terraform_files("terraform")
dependencies = get_dependencies(files)

table_headers = ["resource\ntype", "name", "current\nversion", "latest\navailable", "constraint", "latest\nallowed", "status"]
table = []

for dependency in dependencies:
    available_versions = get_available_versions(dependency["target"], dependency["source"])
    allowed_versions = get_allowed_versions(
        available_versions,
        dependency["lower_constraint"],
        dependency["lower_constraint_operator"],
        dependency["upper_constraint"],
        dependency["upper_constraint_operator"],
    )

    # Versions
    current_version = dependency["version"]
    latest_available_version = get_latest_version(available_versions)
    latest_allowed_version = get_latest_version(allowed_versions)

    status = get_status(current_version, latest_available_version, latest_allowed_version)

    if compare_versions(get_semantic_version(current_version), "!=", get_semantic_version(latest_allowed_version)):
        if dry_run:
            pass
        else:
            update_version(dependency["file_path"], dependency["code"], current_version, latest_allowed_version)
        
    table.append([dependency["target"], dependency["name"], current_version, latest_available_version, dependency["constraint"], latest_allowed_version, status])

print('\n')
if dry_run:
    print("This is a what if scenario.  No files were updated.")
table = tabulate(table, headers=table_headers, tablefmt='orgtbl')
print(table)
print('\n')

env_file = os.getenv('GITHUB_ENV')

with open(env_file, "a") as myfile:
    myfile.write(f"TABLE={table}")
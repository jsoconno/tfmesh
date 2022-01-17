from tfmesh.core import *

dry_run = True

files = get_terraform_files("terraform")
print(files)
resources = get_dependencies(
    files,
    patterns = {
        "terraform": [r'(((terraform)) *{[^}]*?required_version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'],
        "provider": [r'(([a-zA-Z\S]*) *= *{[^}]*?[\s]*source *= *\"(.*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?})'],
        "module": [
            r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\"[\s]*version *= *\"(\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})',
            r'(module *\"(.*)\" *{[^}]*?source *= *\"(\S*)\?ref=([a-zA-Z]*\S*)\" *#? *(([=!><~(.*)]*) *([0-9\.]*) *,* *([=!><~(.*)]*) *([0-9\.]*))[\s\S]*?^})'
        ]
    }
)

table_headers = ["resource\ntype", "module\nname", "current\nversion", "latest\navailable", "constraint", "latest\nallowed", "status"]
table = []

for target, dependencies in resources.items():
    for dependency, data in dependencies.items():
        print(dependency)
        print(data["target"], data["source"])
        available_versions = get_available_versions(data["target"], data["source"])
        print(f'available versions: {available_versions}')
        print('\n')
        allowed_versions = get_allowed_versions(
            available_versions,
            data["lower_constraint"],
            data["lower_constraint_operator"],
            data["upper_constraint"],
            data["upper_constraint_operator"],
        )

        # Versions
        current_version = data["version"]
        latest_available_version = get_latest_version(available_versions)
        latest_allowed_version = get_latest_version(allowed_versions)

        status = get_status(current_version, latest_available_version, latest_allowed_version, no_color=True)

        if compare_versions(get_semantic_version(current_version), "!=", get_semantic_version(latest_allowed_version)):
            if dry_run:
                pass
            else:
                update_version(data["file_path"], data["code"], current_version, latest_allowed_version)
            
        table.append([data["target"], data["name"], current_version, latest_available_version, data["constraint"], latest_allowed_version, status])

print('\n')
if dry_run:
    print("This is a dry run.  No files were updated.")
table = tabulate(table, headers=table_headers, tablefmt='pretty')
print(table)
print('\n')
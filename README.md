# Terraform Mesh

Terraform Mesh is a built-for-purpose Terraform dependency manager that provides a simple and powerful CLI for automating dependency updates that integrates with modern CI/CD processes.

The project is currently under **active development** and aims to eliminate the toil of keeping cloud infrastructure dependencies up-to-date.  In order to test updates to the CLI, make changes and run `pip3 install --editable .` locally.

![Latest tag](https://img.shields.io/github/v/tag/jsoconno/tfmesh)
![Lines of code](https://img.shields.io/tokei/lines/github/jsoconno/tfmesh)

[![codecov](https://codecov.io/gh/Jsoconno/tfmesh/branch/master/graph/badge.svg?token=BW4GBBD7Y5)](https://codecov.io/gh/Jsoconno/tfmesh)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/jsoconno/tfmesh/Publish%20to%20Codecov?label=tests)

![GitHub commit activity](https://img.shields.io/github/commit-activity/y/jsoconno/tfmesh)
![GitHub pull requests](https://img.shields.io/github/issues-pr/jsoconno/tfmesh)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/jsoconno/tfmesh)

![GitHub issues](https://img.shields.io/github/issues/jsoconno/tfmesh)
![GitHub closed issues](https://img.shields.io/github/issues-closed/jsoconno/tfmesh)

![GitHub contributors](https://img.shields.io/github/contributors/jsoconno/tfmesh)

# Selecting files

By default, Terraform Mesh will search for files that match the pattern `'*.tf`.  This will collect all dependencies in the current directory.  In order to recursively collect versioned resources, you can override this value with `**/*.tf`.

# Supported resources

The following Terraform configuration file dependencies are supported.

* Terraform `required_version` block
* Provider `required_providers` blocks
* Terraform Registry (Public and Private)
* Github Modules (Public and Private)

Modules hosted in a git repository work so long as semantic versioning is used (e.g. `1.1.1`, `v1.0.0`, `version1.0.0-pre001`, etc.)  Both https and ssh are supported methods for referencing private modules.

Further development and testing is planned to support `gitlab` and `bitbucket` git sources and tags.

# Version constrains

All version constraints natively available in Terraform are supported.

* `=`: equal to the given version (pinned)
* `!=`: not equal to a given version (excluded)
* `>`: greater than the given version (non-inclusive)
* `>=`: greater than or equal to the given version (inclusive)
* `<`: less than the given version (non-inclusive)
* `<=`: less than or equal to the given version (inclusive)
* `~>`: only the rightmost version component can increment

Upper and lower constraints are also supported (e.g. `>=1.0.0, <2.0.0`).  Both `~>x.x` and `~>x.x.x` are valid for pessimistic constraint operators.

# Setting constraints

Terraform Mesh has taken the approach of using inline comments to set constraints.  For example:

```terraform
terraform {
    required_version = "1.1.3" # >=1.0.0

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "3.71.0" # ~>3.0
        }
    }
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "1.9.0"
        }
    }
}

module "consul" {
  source = "hashicorp/consul/aws"
  version = "0.5.0" # >=0.2.0, <0.6.0
}
```

It is recommended to use Terraform Mesh comment syntax over the Terraform default options (such as specifying the version constraints in the version attribute itself) to give users greater control over when versions are updated.

# Terraform Mesh CLI

The tfmesh cli provides a convenient way of working with version updates in Terraform that is suited for local development or CI/CD pipelines.

## Base command

* `tfmesh` - the root command group.

The following options are supported:

* `--version` - returns the cli version.
* `--help` - returns helpful information.

## Init command

The `init` command creates a yaml file that stores basic information about the files that contain Terraform configurations.

* `tfmesh init` - creates a yaml file used for storing configuration file details.

The following options are supported:

* `--config-file` - the name of the configuration file (defaults to ".tfmesh.yaml")
* `--terraform-folder` - the name of the folder where Terraform files are located (defaults to the current directory).
* `--terraform-file-pattern` - the pattern for matching Terraform files within the directory (defaults to *.tf).
* `--force` - allows for non-interactive reset of the configuration file for automation purposes.

Example:
```cmd
tfmesh init --terraform-folder terraform --force
```

## Get command

The `get` command allows you to retrieve information about resources in your configuration that reference a version.

* `tfmesh get terraform ATTRIBUTE` - returns a given attribute for the Terraform executable (see attributes below).
* `tfmesh get providers` - returns a list of all tracked providers.
* `tfmesh get provider NAME ATTRIBUTE` - returns a given attribute for a specific provider (see attributes below).
* `tfmesh get modules` - returns a list of all tracked modules.
* `tfmesh get module NAME ATTRIBUTE` - returns a given attribute for a specific module (see attributes below).

The following attributes are supported:

* `target` - returns the type of resource being managed.
* `filepath` - returns the absolute path to the Terraform configuration file.
* `filename` - returns the name of the Terraform file.
* `code` - returns the configuration code block.
* `name` - returns the name of the resource.
* `source` - returns the source for the resource.
* `version` - returns the version.
* `versions` - returns a list of available versions.
* `constraint` - returns the full version constraint.
* `lower_constraint_operator` - returns the lower constraint operator (e.g. ">=").
* `lower_constraint` - returns the lower constraint (e.g. "1.0.0").
* `upper_constraint_operator` - returns the upper constraint operator (e.g. "<").
* `upper_constraint` - returns the lower constraint (e.g. "2.0.0").

The following options are supported:

* `--allowed` - returns only allowed versions when used in conjunction with the versions attribute.
* `--exclude-prerelease` - returns all non-prerelease versions when used in conjunction with the versions attribute.
* `--top` - returns the top n number of results when used in conjunction with the versions attribute.

Example:
```cmd
tfmesh get module s3 versions --allowed --exclude-prerelease --top 10
```

## Set command

The `set` command allows you to update your configurations resource versions and constraints.  Versions and constraints are validated to ensure they are set with acceptable values.

* `tfmesh set terraform ATTRIBUTE VALUE` - sets a given attribute for the Terraform executable to a given value (see attributes below).
* `tfmesh set provider NAME ATTRIBUTE VALUE` - sets a given attribute for a specific provider to a given value (see attributes below).
* `tfmesh set module NAME ATTRIBUTE VALUE` - sets a given attribute for a specific module to a given value (see attributes below).

The following attributes are supported:

* `version` - returns the version.
* `constraint` - returns the full version constraint.

The following options are supported:

* `--exclude-prerelease` - ensures the set version is not a pre-release.
* `--what-if` - allows for a dry run to see what would happen before making changes.
* `--ignore-constraints` - allows the version to be set to a valid version that does not meet the defined constraint.
* `--force` - allows the version to be set to any value without validation.

Example:
```cmd
tfmesh set s3 version "1.0.0" --ignore-constraints
```

## Plan command

The `plan` command provides details about what would happen if you applied configuration upgrades.

* `tfmesh plan` - plans what version upgrades will happen.

The following options are supported:

* `--target TYPE NAME` - takes arguments `TYPE` and `NAME` to allow for specific update targets.  For example, `--target provider aws`.  Multiple targets are allowed.
* `--exclude-prerelease` - ensures the set version is not a pre-release.
* `--ignore-constraints` - allows the version to be set to a valid version that does not meet the defined constraint.
* `--no-color` - removes terminal color formatting.

Example:
```cmd
tfmesh plan
```

## Apply command

The `apply` command applies version upgrades to the configuration based on the current versions and constraints.

* `tfmesh apply` - applies version upgrades.

The following options are supported:

* `--target TYPE NAME` - takes arguments `TYPE` and `NAME` to allow for specific update targets.  For example, `--target provider aws`.  Multiple targets are allowed.
* `--exclude-prerelease` - ensures the set version is not a pre-release.
* `--ignore-constraints` - allows the version to be set to a valid version that does not meet the defined constraint.
* `--no-color` - removes terminal color formatting.
* `--auto-approve` - approves upgrades without prompting for user input.

Example:
```cmd
tfmesh apply
```

# Example output

```
+-----------+-------------+--------------+--------------+-----------------+--------------+-------------------------+
| resource  |   module    |   current    |    latest    |   constraint    |    latest    |         status          |
|   type    |    name     |   version    |  available   |                 |   allowed    |                         |
+-----------+-------------+--------------+--------------+-----------------+--------------+-------------------------+
|  modules  |   consul    |    0.5.0     |    0.11.0    |     ~>0.5.0     |    0.5.0     | (.) pinned out-of-date  |
|  modules  | conventions | 6.0.0-pre001 | 6.0.0-pre001 |      ~>6.0      | 6.0.0-pre001 |     (*) up-to-date      |
|  modules  | api_gateway |    v1.0.2    |    v1.0.2    |                 |    v1.0.2    |     (*) up-to-date      |
|  modules  |   lambda    |    v1.1.2    |    v1.1.2    |      ~>1.1      |    v1.1.2    |     (*) up-to-date      |
|  modules  |     s3      |    v1.1.0    |    v1.1.0    | >=1.0.0, <2.0.0 |    v1.1.0    |     (*) up-to-date      |
| terraform |  terraform  |    1.1.3     |    1.1.3     |     >=1.0.0     |    1.1.3     |     (*) up-to-date      |
| providers |     aws     |    3.72.0    |    3.72.0    |     ~>3.70      |    3.72.0    |     (*) up-to-date      |
| providers |   azurerm   |    1.9.0     |    2.92.0    | >=3.0.0, <2.0.0 |              | (x) no suitable version |
+-----------+-------------+--------------+--------------+-----------------+--------------+-------------------------+
```

# Version status

Terraform Mesh will evaluate versions in your configuration to determine the current version, latest available version, and latest allowed version.

* `current version` - The current version set in the configuration.
* `latest available` - The latest available version available for Terraform or a given provider or module.
* `latest allowed` - The latest version that is allowed based on constraints in the configuration.

The supported status are:

* `(*) up-to-date` - The `current version` matches the `latest available version`.
* `(->) upgraded to latest` - The `current version` was upgraded to the `latest available version`.
* `(>)upgraded to allowed` - The `current version` was upgraded to the `latest allowed version` and is behind.
* `(<-) downgraded to latest` - The `current version` was downgraded to the `latest available version`.
* `(<) downgraded to allowed` - The `current version` was downgraded to the `latest allowed version` and is behind.
* `(.) pinned out-of-date` - The `current version` is pinned and is behind.
* `(x) no suitable version` - The was no available version that met the provided constraints.
# Terraform Mesh

Terraform Mesh is a built-for-purpose Terraform dependency manager that provides a simple and powerful CLI for automating dependency updates that integrates with modern CI/CD processes.

The project is currently under **active development** and aims to eliminate the toil of keeping cloud infrastructure dependencies up-to-date

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

# Selecting Files

By default, Terraform Mesh will search for files that match the pattern `'*.tf`.  This will collect all dependencies in the current directory.  In order to recursively collect versioned resources, you can override this value with `**/*.tf`.

# Supported Resources

The following Terraform configuration file dependencies are supported.

* Terraform `required_veresion` block
* Provider `required_providers` blocks
* Terraform Registry (Public and Private)
* Github Modules (Public and Private)

Modules hosted in a git repository work so long as semantic verioning is used (e.g. `1.1.1`, `v1.0.0`, `version1.0.0-pre001`, etc.)  Both https and ssh are supported methods for referencing private modules.

Further development and testing is planned to support `gitlab` and `bitbucket` git sources and tags.

# Version Constrains

All version contraints natively available in Terraform are supported.

* `=`: equal to the given version (pinned)
* `!=`: not equal to a given version (excluded)
* `>`: greater than the given version (non-inclusive)
* `>=`: greater than or equal to the given version (inclusive)
* `<`: less than the given version (non-inclusive)
* `<=`: less than or equal to the given version (inclusive)
* `~>`: only the rightmost version component can increment

Upper and lower constraints are also supported (e.g. `>=1.0.0, <2.0.0`).  Both `~>x.x` and `~>x.x.x` are valid for pessimistic contraint operators.

# Setting Constraints

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
* `tfmesh` - this would be the root command.
  * `--version` - returns the cli version.
  * `--help` - returns helpful information.

## Get command
* `get` - action for getting information about the configuration and config versions.
  * `terraform` - returns all details about the terraform executable.
    * `--filepath` - returns the absolute path to the Terraform configuration file.
    * `--file` - returns the name of the Terraform file.
    * `--code` - returns the configuration code block.
    * `--source` - returns the source for the resource.
    * `--version` - returns the version.
    * `--constraints` - returns version constraints.
    * `--available-verions` - returns available versions.
    * `--allowed-versions` - returns allowed versions based on constraints.
  * `provider` - returns a list of tracked providers.
    * `name (optional)` - returns all details about a given provider.
      * `--filepath` - returns the absolute path to the Terraform configuration file.
      * `--file` - returns the name of the Terraform file.
      * `--code` - returns the configuration code block.
      * `--source` - returns the source for the resource.
      * `--version` - returns the version.
      * `--constraints` - returns version constraints.
      * `--available-verions` - returns available versions.
      * `--allowed-versions` - returns allowed versions based on constraints.
  * `module` - returns a list of tracked modules.
    * `name (optional)` - returns all details about a given module.
      * `--filepath` - returns the absolute path to the Terraform configuration file.
      * `--file` - returns the name of the Terraform file.
      * `--code` - returns the configuration code block.
      * `--source` - returns the source for the resource.
      * `--version` - returns the version.
      * `--constraints` - returns version constraints.
      * `--available-verions` - returns available versions.
      * `--allowed-versions` - returns allowed versions.

Example:
```cmd
tfmesh get module s3 --constraints
```

## Set command
* `set` - action for setting terraform versions and constraints.
  * `terraform`
    * `--version`
    * `--constraint`
  * `provider`
    * `name`
      * `--version`
      * `--constraint`
  * `module`
    * `name`
      * `--version`
      * `--constraint`

Example:
```cmd
tfmesh set s3 --version 1.0.0
```

## Upgrade command
* `upgrade` - action for upgrading terraform versions based on constraints.
  * `all` - updates all terraform, providers, and modules.
  * `terraform` - updates terraform.
  * `provider` - updates providers.
  * `module` - updates modules.

All commands support a `--dry-run` flag that will provide terminal output of what would happen if the update command was ran.  They also support a `--verbose` flag that outputs additional configuration information to the terminal.

Example:
```cmd
tfmesh upgade all
```

# Example Output
```
+-------------------+-------------+---------+-----------+-----------------+---------+-------------------------+
|     resource      |   module    | current |  latest   |   constraint    | latest  |         status          |
|       type        |    name     | version | available |                 | allowed |                         |
+-------------------+-------------+---------+-----------+-----------------+---------+-------------------------+
| module (registry) |   consul    |  0.5.0  |  0.11.0   | >=0.2.0, <0.6.0 |  0.5.0  | (.) pinned out-of-date  |
| module (registry) | conventions |  6.0.0  |   6.0.0   |     >=5.0.0     |  6.0.0  |     (*) up-to-date      |
|     terraform     |  terraform  |  1.1.3  |   1.1.3   |     >=1.0.0     |  1.1.3  |     (*) up-to-date      |
|     provider      |     aws     | 3.71.0  |  3.71.0   |      ~>3.0      | 3.71.0  |     (*) up-to-date      |
|     provider      |   azurerm   |  1.9.0  |  2.91.0   | >=3.0.0, <2.0.0 |         | (x) no suitable version |
+-------------------+-------------+---------+-----------+-----------------+---------+-------------------------+
```

# Version Status
TFMesh will evaluate versions in your configuration to determine the current version, latest available version, and latest allowed version.

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
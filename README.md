# Terraform Mesh
Terraform Mesh is a built-for-purpose Terraform dependency manager that provides a simple and powerful CLI for automating dependency updates that integrates with modern CI/CD processes.

The project is currently under **active development** and aims to eliminate the toil of keeping cloud infrastructure dependencies up-to-date

# Badges
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

# TFMesh CLI
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
    * `--version` - returns the version.
    * `--constraints` - returns version constraints.
    * `--allowed-versions` - returns allowed versions based on constraints.
  * `provider` - returns a list of tracked providers.
    * `name (optional)` - returns all details about a given provider.
      * `--filepath` - returns the absolute path to the Terraform configuration file.
      * `--file` - returns the name of the Terraform file.
      * `--code` - returns the configuration code block.
      * `--version` - returns the version.
      * `--constraints` - returns version constraints.
      * `--allowed-versions` - returns allowed versions based on constraints.
  * `module` - returns a list of tracked modules.
    * `name (optional)` - returns all details about a given module.
      * `--filepath` - returns the absolute path to the Terraform configuration file.
      * `--file` - returns the name of the Terraform file.
      * `--code` - returns the configuration code block.
      * `--version` - returns the version.
      * `--constraints` - returns version constraints.
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
| target            | name        | config version   | constraint      | latest version   | status         |
|-------------------+-------------+------------------+-----------------+------------------+----------------|
| module (registry) | consul      | 0.5.0            | >=0.2.0, <0.6.0 |                  | up-to-date     |
| module (registry) | conventions | 1.0.1            | ~>0.4.0         | 0.4.1            | downgraded     |
| module (git)      | api_gateway | v1.0.2           |                 |                  | up-to-date     |
| module (git)      | lambda      | v1.0.2           | >=1.0.0, <2.0.0 | v1.1.2           | upgraded       |
| module (git)      | s3          | v1.1.0           | ~>1.0           |                  | up-to-date     |
| terraform         | terraform   | 1.0.0            |                 | 1.1.2            | pinned - stale |
| provider          | aws         | 3.3.0            | ~>3.0           | 3.9.0            | upgraded       |
| provider          | aws         | 1.9.0            | >=1.9.0, <2.0.0 |                  | up-to-date     |
```

# Version Status
TFMesh will evaluate versions in your configuration to determine the current version, latest available version, and latest allowed version.

* `current version` - The current version set in the configuration.
* `latest available version` - The latest available version available for Terraform or a given provider or module.
* `latest allowed version` - The latest version that is allowed based on constraints in the configuration.

The supported status are:

* `(*) up-to-date` - The `current version` matches the `latest available version`.
* `(->) upgraded to latest` - The `current version` was upgraded to the `latest available version`.
* `(>)upgraded to allowed` - The `current version` was upgraded to the `latest allowed version` and is behind.
* `(<-) downgraded to latest` - The `current version` was downgraded to the `latest available version`.
* `(<) downgraded to allowed` - The `current version` was downgraded to the `latest allowed version` and is behind.
* `(.) pinned out-of-date` - The `current version` is pinned and is behind.
* `(x) no suitable version` - The was no available version that met the provided constraints.
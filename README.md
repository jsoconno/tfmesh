# TFMesh
The built-for-purpose Terraform dependency manager.  TFMesh provides a simple and powerful CLI that allows you to get configuration version details and make updates that naturally integrates with current CI/CD processes.

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

# Development Roadmap
This project is under active development.  This section outlines the capability roadmap for TFMesh.  This will be taken down once the initial version of the tool is released into the wild.

Desired outcomes are:
1. A working CLI that can run locally or in a pipeline
2. A Github action that can automatically make code changes and raise a PR based on user-defined triggers

## Overview
Code will be written that can:
* Read Terraform files
* Parse the files to get current versions for terraform, providers, and modules
* Check against the source (public and private) for updates
* Allow users to set version constraints with familiar Terraform syntax
* Compare versions against constraints to get a list of valid versions for the configuration
* Update Terraform configuration files based on the latest valid version that meets constraints

## Read Terraform Files
Feature requirements:
* User can input a path to the Terraform directory.  Default to `root`.
* All files in the Terraform file directory with a given file pattern are read.  Default to `*.tf`.

## Get User Specified Versions
Feature requirements:
* Files can be parsed in a standard way
* Parsing results in details about the configuration
  * `type` = `terraform`, `provider`, or `module`.
  * `name` = `terraform`, `aws`, `azurerm`, `some_module`
  * `source` = `registry`, `github`, `bitbucket`, `s3`, etc.
  * `version` = e.g. `1.0.1` or `2.0.0`
  * `constraint` = `>= 1.0`, `~> 1.1.0`, `>= 1.0.0 , < 2.0.0`, etc.

## Check Against Source
Feature requirements:
* API's can be hit to get a list of all available tags.  For example, Terraform registry, GitHub, etc.
* PAT tokens or other auth methods can be used to allow reading from private repos when checking versions.

## Take Into Account User Constraints
Feature requirements:
* Allow special comments or configuration files to set constraints using Terraform's existing syntax.
* Allow for global constrains including:
  * `max_bump` - values can be `major`, `minor`, or `patch`.
  * `allow_prerelease` - default is True.
  * `patch_versions_behind` - number
  * `minor_versions_behind` - number
  * `patch_versions_behind` - number
* Create logic that can determine the minimum and maximium verions based on constraints.

## Compare Versions
Feature requirements:
* Create a list of allowed versions based on constraints.
* Evaluate current versions against allowed versions.
* Identify the version that will be used in the update.

## Update Code in Pipeline
Feature requirements:
* Make automated code changes to use the latest allowed version based on constraints.
* Output details about what is getting bumped to the terminal.
* Push those code changes to a user defined branch.  Default to `automated-terraform-version-updates`.

## Raise a Pull Request
* Raise a pull request in the Git repo where the Terraform code lives

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
* `(.) version pinned` - The `current version` is pinned and is behind.
* `(x) no suitable version` - The was no available version that met the provided constraints.

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
  * `providers` - returns a list of tracked providers.
    * `name (optional)` - returns all details about a given provider.
      * `--filepath` - returns the absolute path to the Terraform configuration file.
      * `--file` - returns the name of the Terraform file.
      * `--code` - returns the configuration code block.
      * `--version` - returns the version.
      * `--constraints` - returns version constraints.
      * `--allowed-versions` - returns allowed versions based on constraints.
  * `modules` - returns a list of tracked modules.
    * `name (optional)` - returns all details about a given module.
      * `--filepath` - returns the absolute path to the Terraform configuration file.
      * `--file` - returns the name of the Terraform file.
      * `--code` - returns the configuration code block.
      * `--version` - returns the version.
      * `--constraints` - returns version constraints.
      * `--allowed-versions` - returns allowed versions.

Example:
```cmd
tfmesh get modules s3 --constraints
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
  * `providers` - updates providers.
  * `modules` - updates modules.

All commands support a `--what-if` flag that will provide terminal output of what would happen if the update command was ran.  They also support a `--verbose` flag that outputs additional configuration information to the terminal.

Example:
```cmd
tfmesh update all
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
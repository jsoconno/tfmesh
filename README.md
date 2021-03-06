# Terraform Mesh

A mesh is an interlaced structure. A network of interconnected things. As a verb, it can mean to be locked together or engaged with another. One way these descriptions can be manifested in Cloud Engineering is in the various dependencies that go into an infrastructure configuration. Dependency management is an important topic when thinking about how you mature, scale, and secure your automated cloud deployments.  

**Terraform Mesh** (or tfmesh for short) is an open source command line interface tool designed to make Terraform version management simple and effective.  It integrates beautifully with you preferred ways of working locally, pre-commit hooks, and CI/CD pipelines.  The tool supports all Terraform native version constraint operators as well as public and private sources for providers and modules.

The project is currently under **active development** and aims to the preferred choice for App Developers and Cloud Engineers working with Terraform as an infrastructure-as-code platform.

To test the command line interface, you can run the following from the root folder locally:

```cmd
pip3 install --editable .
```

From there you can start to run `tfmesh` commands.

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

Terraform Mesh will collect all versioned resources within the current working directory with the file extension `*.tf` by default.  This is similar to the way Terraform works by default as well.

You can change the files selected using the `--terraform-folder` and `--terraform-file-pattern` options.  For example, if you were in the root folder and you wanted to collect all versioned resources from a child folder named `terraform` you could run the following command:

```cmd
tfmesh get providers --terraform-folder terraform
```

If you wanted to collect all `.tf` files under the `terraform` folder AND all of its children you could run the following command:
```cmd
tfmesh get providers --terraform-folder terraform --terraform-file-pattern "**/*.tf"
```

# Supported resources

The following Terraform configuration file dependencies are supported.

* Terraform `required_version` block
* Provider `required_providers` blocks
* Terraform Registry (Public and Private)
* Github Modules (Public and Private)
* Azure DevOps Modules (Public and Private)

Modules hosted in a git repository work so long as semantic versioning is used (e.g. `1.1.1`, `v1.0.0`, `version1.0.0-pre001`, etc.)  Both https and ssh are supported methods for referencing private modules.

Further development and testing is planned to support `gitlab` and `bitbucket` git sources and tags.

# Version constraints

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

It is also recommended to make all updates to versions and constraints using the `set` commands packaged with the Terraform Mesh CLI.

# Terraform Mesh CLI

The tfmesh cli provides a convenient way of working with version updates in Terraform that is suited for local development or CI/CD pipelines.

## Universal options

The following options are available for all commands.

* `--terraform-folder` - the name of the folder where Terraform files are located (defaults to the current directory).
* `--terraform-file-pattern` - the pattern for matching Terraform files within the directory (defaults to *.tf).
* `--var` - one or more variables to be added to the configuration file in the format `some=value`.

## Base command

* `tfmesh` - the root command group.

The following options are supported:

* `--version` - returns the cli version.
* `--help` - returns helpful information.

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

Don't worry if you forget the available attributes while using the tool on the command line.  Terraform Mesh will help you out with hints if you misspell or fail to provide an attribute.

## Set command

The `set` command allows you to update your configurations resource versions and constraints.  Versions and constraints are validated to ensure they are set with acceptable values.

* `tfmesh set terraform ATTRIBUTE VALUE` - sets a given attribute for the Terraform executable to a given value (see attributes below).
* `tfmesh set provider NAME ATTRIBUTE VALUE` - sets a given attribute for a specific provider to a given value (see attributes below).
* `tfmesh set module NAME ATTRIBUTE VALUE` - sets a given attribute for a specific module to a given value (see attributes below).

The following attributes are supported:

* `version` - sets the version.
* `constraint` - sets the full version constraint.

The following options are supported:

* `--exclude-prerelease` - ensures the set version is not a pre-release.
* `--what-if` - allows for a dry run to see what would happen before making changes.
* `--ignore-constraints` - allows the version to be set to a valid version that does not meet the defined constraint.
* `--force` - allows the version to be set to any value without validation.

Example:
```cmd
tfmesh set module s3 version "1.0.0" --ignore-constraints
```

## Plan command

The `plan` command provides details about what would happen if you applied configuration upgrades.

* `tfmesh plan` - plans what version upgrades will happen.

The following options are supported:

* `--target TYPE NAME` - takes arguments `TYPE` and `NAME` to allow for specific update targets.  For example, `--target provider aws`.  Multiple targets are allowed.
* `--exclude-prerelease` - ensures the set version is not a pre-release.
* `--ignore-constraints` - allows the version to be set to a valid version that does not meet the defined constraint.
* `--no-color` - removes terminal color formatting, primarily for automation purposes.
* `--verbose` - returns all resources including those with no version changes.

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
* `--no-color` - removes terminal color formatting, primarily for automation purposes.
* `--verbose` - returns all resources including those with no version changes.
* `--auto-approve` - approves upgrades without prompting for user input.

Example:
```cmd
tfmesh apply
```

# Version status

Resource actions and version statuses are indicated with the following symbols in plan and apply:

Actions:
* `+`: upgraded - the version will be or was upgraded.
* `-`: downgraded - the version will be or was downgraded.
* `~`: no change - the version was unchanged.

Version status:
* `*`: latest available version - the version will be or is the latest available.
* `.`: latest allowed version - the version will be or is the latest allowed version.
* `x`: no suitable version - there was no suitable version based on constraints.
* `!`: bug - you found a bug (please report on GitHub).

Actions and and versions are used together separated by a forward slash (/) to indicate changes.
For example, `+/*` would indicate the version will be upgraded to the latest version

# Example output

```
Resource actions and version statuses are indicated with the following symbols:


Actions:
+: upgraded
-: downgraded
~: no change


Version status:
*: latest available version
.: latest allowed version based on constraints
x: no suitable version
!: bug


Actions and and versions are used together separated by a forward slash (`/`) to indicate changes.
For example, '+/*' would indicate the version will be upgraded to the latest version


Terraform Mesh will perform the following actions:

terraform {
-/. required_version = "1.1.4" # =1.0.0 // downgrade to latest allowed = 1.0.0


aws = {
    source = "hashicorp/aws"
+/* version = "3.72.0" # ~>3.0 // upgrade to latest available = 3.73.0
}


Plan: 1 to upgrade, 1 to downgrade
```
# Setting variables

Variables allow users to pass data to Terraform Mesh, primarily for authenticating with private repositories.  If the same variable is assigned multiple values, Terraform Mesh uses the last value it finds, overriding any previous values.  Variables set on the command line will always take precedence over variables set directly as environment variables.

Setting variables on the command line:

```cmd
tfmesh get module s3 versions --var="github_token=xxxxxxxxxxxxxxxx"
```

Setting variables directly as environment variables:
```cmd
export TFMESH_GITHUB_TOKEN=xxxxxxxxxxxxxxxx
```

Valid variable names only use alphanumerics and underscores.  Any non-alphanumeric characters will be removed and dashes converted to underscores when the variable is processed.

For example, setting a variable like `--var="som3-v@r=this"` would be converted on the backend to `TFMESH_SOM_VR=this` because:
* `TFMESH_` would be prefixed
* The `3` at `@` symbol would be stripped and
* The dash (`-`) converted to an underscore (`_`).

This behavior is primarily to ensure that valid environment variables are set.  By default, all options can be set on the command line by exporting an environment variable that is prefixed with `TFMESH_`.

# Authentication

The primary way that Terraform Mesh interacts with other private git repositories is through the user of personal access tokens (PAT).  For each supported private provider or module source a PAT must be provided.

Supported private git repositories:
* GitHub - use the `github_token` variable or `TFMESH_GITHUB_TOKEN` environment variable.
* Azure DevOps - use the `azure_devops_token` variable or `TFMESH_AZURE_DEVOPS_TOKEN` environment variable.

To manage resource versions from a private repo, the appropriate token variable must be set.  This can be done on the command line at runtime using the `--var` flag in combination with any command or by setting the environment variable directly on the terminal as described in the setting variables section of the docs.

# Handling errors

Support was added to allow users to see when a resource that is located in a private repo is not accessible for some reason.

Below are the common errors and what they most likely mean.

* **203 Non-Authoritative Information** - the authentication token (PAT) for the target repository is not set or is in the wrong format.
* **404 Not Found** - the authentication token (PAT) for the target repository is not set.
* **401 Not Unauthorized** - the authentication token (PAT) for the target repository set to in incorrect value or the token is expired.

For more information on setting variables, see the setting variables section of the docs.
# This file is used for running tests of the get_dependency_attributes function.

terraform {
    required_version = "1.1.3"

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "3.71.0" # ~>3.0
        }
    }
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "1.9.0" # >=3.0.0, <2.0.0
        }
    }
}

module "consul" {
  source = "hashicorp/consul/aws"
  version = "0.5.0" # >=0.2.0, <0.6.0
}

module "s3" {
  source = "github.com/jsoconno/terraform-module-aws-s3?ref=v1.1.0" # >=1.0.0

  s3_access_iam_role_names = [
      module.lambda.role_name
  ]

  tags = var.tags
}
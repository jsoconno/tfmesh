terraform {
    required_version = "1.0.11" # ~>1.0.0

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
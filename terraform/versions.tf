terraform {
    required_version = "1.1.3" # >=1.0.0

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "3.72.0" # ~>3.0
        }
    }
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "2.90.0" # =2.90.0
        }
    }
}
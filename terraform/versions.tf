terraform {
    required_version = "1.0.0" # =1.0.0

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "3.73.0" # ~>3.0
        }
    }
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "2.88.0" # >3.0.0, <2.0.0
        }
    }
}
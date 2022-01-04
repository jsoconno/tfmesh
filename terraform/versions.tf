terraform {
    

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "3.9.0" # ~>3.0
        }
    }
    required_providers {
        aws = {
            source = "hashicorp/azurerm"
            version = "1.9.0" # >=1.9.0, <2.0.0
        }
    }
}
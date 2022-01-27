terraform {
    required_version = "1.1.4" # >=1.1.1

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "3.73.0" # >=3.0.0, <4.0.0
        }
        azurerm = {
            source = "hashicorp/azurerm"
            version = "2.93.1" # >1.1.0
        }
    }
}
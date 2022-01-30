terraform {
    required_version = "1.1.4" # >1.1.3

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "3.74.0" # <=3.0.0, >4.0.0
        }
        azurerm = {
            source = "hashicorp/azurerm"
            version = "1.5.0" # =1.1.0
        }
    }
}
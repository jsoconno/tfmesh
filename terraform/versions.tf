terraform {
    required_version = "1.3.0-alpha20220622" # ~>1.0

    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "3.75.2" # >=3.0.0, <4.0.0
        }
        azurerm = {
            source = "hashicorp/azurerm"
            version = "1.1.0" # =1.1.0
        }
    }
}
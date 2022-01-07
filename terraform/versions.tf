terraform {
    required_version = "1.1.3"

    required_providers {
        aws = {
            source = "hashicorp/aws"
<<<<<<< HEAD
            version = "3.60.0" # ~>3.0
=======
            version = "3.70.0" # ~>3.0
>>>>>>> ce2808172907f4e26f19ac7006d60ffbf424536a
        }
    }
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "1.9.0" # >=3.0.0, <2.0.0
        }
    }
}
module "consul" {
  source = "hashicorp/consul/aws"
  version = "0.5.0" # >=0.2.0, <0.6.0
}

module "conventions" {
  source  = "Jsoconno/conventions/azure"
  version = "6.0.0"
  # insert the 1 required variable here
}

module "consul" {
  source = "git@github.com:hashicorp/example.git"
}
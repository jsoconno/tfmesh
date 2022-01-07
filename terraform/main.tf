module "consul" {
  source = "hashicorp/consul/aws"
  version = "0.3.0" # ~>0.5
}

module "conventions" {
  source  = "Jsoconno/conventions/azure"
  version = "4.0.1" # >=5.0.0
  # insert the 1 required variable here
}

module "consul" {
  source = "git@github.com:hashicorp/example.git"
}
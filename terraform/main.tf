module "consul" {
  source = "hashicorp/consul/aws"
  version = "0.10.0" # ~>0.5
}

module "conventions" {
  source  = "Jsoconno/conventions/azure"
  version = "0.5.1" # ~>6.0
  # insert the 1 required variable here
}

module "consul" {
  source = "git@github.com:hashicorp/example.git"
}

module "api_gateway" {
  source = "github.com/jsoconno/terraform-module-aws-api-gateway?ref=v1.0.2"
    # source = "../terraform-module-aws-api-gateway"

  name = "test-api-gateway"
  body = local.body

  tags = var.tags
}

module "lambda" {
  source = "github.com/jsoconno/terraform-module-aws-lambda?ref=v1.1.2" # ~>1.1
  #   source = "../terraform-module-aws-lambda"

  name = "test-lambda"

  environment_variables = {
    REGION = data.aws_region.current.name
    BUCKET = module.s3.id
  }

  api_gateway_source_arns = [
    module.api_gateway.execution_arn
  ]

  tags = var.tags
}

module "s3" {
  source = "github.com/jsoconno/terraform-module-aws-s3?ref=v1.1.0" # >=1.0.0, <2.0.0
# source = "../terraform-module-aws-s3"

  s3_access_iam_role_names = [
      module.lambda.role_name
  ]

  tags = var.tags
}
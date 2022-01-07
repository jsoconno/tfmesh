data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

locals {
  body = jsonencode({
    swagger = "2.0"
    info = {
      title   = "Example"
      version = "1.0"
    }
    schemes = [
      "https"
    ]
    paths = {
      "/path" = {
        get = {
          responses = {
            "200" = {
              description = "200 response"
            }
          }
          x-amazon-apigateway-integration = {
            type       = "AWS"
            uri        = module.lambda.invoke_arn
            httpMethod = "POST"
            responses = {
              default = {
                statusCode = 200
              }
            }
          }
        }
      }
    }
  })
}

module "api_gateway" {
  source = "github.com/jsoconno/terraform-module-aws-api-gateway?ref=v1.0.2"
    # source = "../terraform-module-aws-api-gateway"

  name = "test-api-gateway"
  body = local.body

  tags = var.tags
}

module "lambda" {
  source = "github.com/jsoconno/terraform-module-aws-lambda?ref=v1.1.1" # >=1.0.0, <1.1.2
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

module "consul" {
  source = "hashicorp/consul/aws"
  version = "0.5.0" # >=0.2.0, <0.6.0
}

module "conventions" {
  source  = "Jsoconno/conventions/azure"
  version = "5.0.0"
  # insert the 1 required variable here
}

# module "consul" {
#   source = "app.terraform.io/example-corp/k8s-cluster/azurerm"
#   version = "1.1.0"
# }

module "consul" {
  source = "git@github.com:hashicorp/example.git"
}

module "s3" {
  source = "github.com/jsoconno/terraform-module-aws-s3?ref=v1.1.0" # >=1.0.0
# source = "../terraform-module-aws-s3"

  s3_access_iam_role_names = [
      module.lambda.role_name
  ]

  tags = var.tags
}
# AWS European Sovereign Cloud stack (Blueprint §4). Separate partition: aws-eusc.
# Use separate accounts, organization, IAM, endpoints and automation from commercial AWS.
terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 6.0" }
  }
  # State MUST live inside the EU sovereign boundary.
  backend "s3" {}
}

provider "aws" {
  region = var.region # verify the Region code published for your EUSC landing zone
  default_tags { tags = { "sovereign:domain" = "aws-eusc", "sovereign:use-case" = var.use_case_id } }
}

data "aws_partition" "this" {}
data "aws_caller_identity" "this" {}

# Fail fast if credentials point at the commercial partition (acceptance criterion §14).
resource "terraform_data" "partition_guard" {
  lifecycle {
    precondition {
      condition     = data.aws_partition.this.partition == "aws-eusc"
      error_message = "Refusing to deploy: credentials are not in the aws-eusc partition."
    }
  }
}

resource "aws_kms_key" "ai" {
  description         = "EUSC CMK for ${var.use_case_id}"
  enable_key_rotation = true
}

resource "aws_iam_role" "workload" {
  name = "${var.use_case_id}-eusc-ai-workload"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.${data.aws_partition.this.dns_suffix}" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy" "invoke" {
  role = aws_iam_role.workload.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = ["bedrock:InvokeModel", "bedrock:Converse"],
      Resource = [for m in var.approved_model_ids : "arn:${data.aws_partition.this.partition}:bedrock:${var.region}::foundation-model/${m}"] }]
  })
}

resource "aws_vpc_endpoint" "bedrock_runtime" {
  vpc_id              = var.vpc_id
  service_name        = var.bedrock_runtime_endpoint_service
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.private_subnet_ids
  private_dns_enabled = true
}

resource "aws_cloudtrail" "ai" {
  name                       = "${var.use_case_id}-eusc-trail"
  s3_bucket_name             = var.evidence_bucket
  kms_key_id                 = aws_kms_key.ai.arn
  enable_log_file_validation = true
}

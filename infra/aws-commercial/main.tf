# AWS commercial public cloud AI stack (Blueprint §3)
terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.80" }
  }
}

provider "aws" {
  region = var.region
  default_tags { tags = { "sovereign:domain" = "aws-commercial", "sovereign:use-case" = var.use_case_id } }
}

data "aws_caller_identity" "this" {}
data "aws_partition" "this" {}

# ---- Keys: customer-managed, scoped to the AI workload role -----------------
resource "aws_kms_key" "ai" {
  description             = "CMK for ${var.use_case_id} prompts, traces, KB and evidence"
  enable_key_rotation     = true
  deletion_window_in_days = 30
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Sid = "Admin", Effect = "Allow", Principal = { AWS = "arn:${data.aws_partition.this.partition}:iam::${data.aws_caller_identity.this.account_id}:root" }, Action = "kms:*", Resource = "*" },
      { Sid = "WorkloadUse", Effect = "Allow", Principal = { AWS = aws_iam_role.workload.arn },
        Action = ["kms:Decrypt", "kms:GenerateDataKey*", "kms:DescribeKey"], Resource = "*",
        Condition = { StringEquals = { "kms:ViaService" = ["s3.${var.region}.amazonaws.com", "bedrock.${var.region}.amazonaws.com"] } } }
    ]
  })
}

# ---- Workload identity -------------------------------------------------------
resource "aws_iam_role" "workload" {
  name = "${var.use_case_id}-ai-workload"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = var.workload_service_principal }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy" "invoke_approved_models_only" {
  role = aws_iam_role.workload.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Sid = "InvokeApproved", Effect = "Allow",
        Action   = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:Converse", "bedrock:ConverseStream"],
        Resource = concat(var.approved_model_arns, var.approved_inference_profile_arns) },
      { Sid = "Guardrail", Effect = "Allow", Action = ["bedrock:ApplyGuardrail"], Resource = aws_bedrock_guardrail.this.guardrail_arn }
    ]
  })
}

# ---- Private connectivity ----------------------------------------------------
resource "aws_vpc_endpoint" "bedrock_runtime" {
  vpc_id              = var.vpc_id
  service_name        = "com.amazonaws.${var.region}.bedrock-runtime"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.private_subnet_ids
  security_group_ids  = var.endpoint_security_group_ids
  private_dns_enabled = true
  policy = jsonencode({
    Statement = [{ Effect = "Allow", Principal = { AWS = aws_iam_role.workload.arn }, Action = "bedrock:*",
      Resource = concat(var.approved_model_arns, var.approved_inference_profile_arns, [aws_bedrock_guardrail.this.guardrail_arn]) }]
  })
}

# ---- Runtime protection ------------------------------------------------------
resource "aws_bedrock_guardrail" "this" {
  name                      = "${var.use_case_id}-guardrail"
  blocked_input_messaging   = "This request is not permitted by enterprise AI policy."
  blocked_outputs_messaging = "The response was blocked by enterprise AI policy."
  kms_key_arn               = aws_kms_key.ai.arn

  content_policy_config {
    filters_config { type = "PROMPT_ATTACK", input_strength = "HIGH", output_strength = "NONE" }
    filters_config { type = "MISCONDUCT", input_strength = "HIGH", output_strength = "HIGH" }
  }
  sensitive_information_policy_config {
    pii_entities_config { type = "EMAIL", action = "ANONYMIZE" }
    pii_entities_config { type = "CREDIT_DEBIT_CARD_NUMBER", action = "BLOCK" }
  }
}

# ---- Audit -------------------------------------------------------------------
resource "aws_s3_bucket" "evidence" {
  bucket        = "${var.use_case_id}-ai-evidence-${data.aws_caller_identity.this.account_id}"
  force_destroy = false
}

resource "aws_s3_bucket_object_lock_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule {
    default_retention {
      mode = "COMPLIANCE"
      days = var.evidence_retention_days
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.ai.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "evidence" {
  bucket                  = aws_s3_bucket.evidence.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudtrail" "ai" {
  name                          = "${var.use_case_id}-ai-trail"
  s3_bucket_name                = aws_s3_bucket.evidence.id
  kms_key_id                    = aws_kms_key.ai.arn
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
}

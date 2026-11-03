output "workload_role_arn" { value = aws_iam_role.workload.arn }
output "kms_key_arn" { value = aws_kms_key.ai.arn }
output "guardrail_arn" { value = aws_bedrock_guardrail.this.guardrail_arn }
output "evidence_bucket" { value = aws_s3_bucket.evidence.id }

variable "region" {
  type        = string
  description = "EUSC Region code (verify in the EUSC console / documentation)"
}
variable "use_case_id" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "evidence_bucket" { type = string }
variable "approved_model_ids" {
  type        = list(string)
  description = "Models verified as available in the selected EUSC Region — names shared with commercial AWS do not imply parity"
}
variable "bedrock_runtime_endpoint_service" {
  type        = string
  description = "Interface endpoint service name for bedrock-runtime in the EUSC Region"
}

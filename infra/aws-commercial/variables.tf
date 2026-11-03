variable "region" {
  type        = string
  description = "Approved home Region for the use case"
}
variable "use_case_id" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "endpoint_security_group_ids" { type = list(string) }
variable "workload_service_principal" {
  type    = string
  default = "ecs-tasks.amazonaws.com"
}
variable "approved_model_arns" {
  type        = list(string)
  description = "Foundation-model ARNs approved in the sovereignty profile"
}
variable "approved_inference_profile_arns" {
  type        = list(string)
  default     = []
  description = "Only inference profiles whose full destination set is approved (in-Region or eligible geographic profile)"
}
variable "evidence_retention_days" {
  type    = number
  default = 2555
}

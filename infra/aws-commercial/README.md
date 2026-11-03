# AWS commercial public cloud domain

Terraform for the AI workload account of the landing zone (Blueprint §3):
customer-managed KMS key, scoped workload role that can invoke **only approved model /
inference-profile ARNs**, Bedrock runtime interface endpoint (PrivateLink), Bedrock
Guardrail, Object-Lock evidence bucket and CloudTrail with log-file validation.

`scp-ai-boundary.json` is an Organizations SCP template for the AI OU. Before applying:

1. Replace `APPROVED-MODEL-ID` and the Region list with the sovereignty-profile values.
2. If you approve a *geographic* inference profile (e.g. `eu.`), the SCP must **not** block
   any destination Region that profile uses, or the profile becomes unavailable. Approve the
   full destination set and the failure behavior (Blueprint §3, [R2], [R20]).
3. Country-only profiles must use in-Region invocation or an eligible country profile.

```bash
terraform init && terraform plan -var-file=env/prod.tfvars
```

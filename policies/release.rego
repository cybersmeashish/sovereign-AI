# Release gate (Blueprint §10, Table 3). Input = verified release manifest + target.
package sovereign.release

import rego.v1

default allow := false

required_components := {"model", "embedding_model", "retrieval_config", "prompt_template", "safety_policy", "tool_definitions", "evaluation_suite"}

gates := {"data_eligibility", "model_eligibility", "application_readiness", "production_placement"}

deny contains "signature not verified" if not input.signature_verified

deny contains sprintf("missing component %s", [c]) if {
	some c in required_components
	not input.manifest.components[c]
}

deny contains sprintf("gate %s not approved", [g]) if {
	some g in gates
	not input.manifest.approvals[g]
}

deny contains "destination not approved" if not input.target in input.manifest.approved_domains

deny contains "release authorization expired" if time.parse_rfc3339_ns(input.manifest.expires_at) <= time.now_ns()

allow if count(deny) == 0

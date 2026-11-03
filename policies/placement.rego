# Placement policy (Blueprint §3, §11). Evaluated before any processing.
package sovereign.placement

import rego.v1

default allow := false

data_classes := ["public", "internal", "confidential", "restricted"]

rank(c) := i if data_classes[i] == c

profile := data.profiles[input.use_case_id]

endpoint := data.endpoints[input.endpoint_id]

deny contains "unknown use case" if not profile

deny contains "unknown endpoint" if not endpoint

deny contains "caller not entitled" if not input.caller_entitled

deny contains msg if {
	not endpoint.domain in profile.permitted_domains
	msg := sprintf("domain %s not permitted", [endpoint.domain])
}

deny contains msg if {
	some j in endpoint.processing_jurisdictions
	not j in profile.permitted_jurisdictions
	msg := sprintf("endpoint may process in unapproved jurisdiction %s", [j])
}

deny contains "country-only profile forbids multi-jurisdiction endpoint" if {
	profile.country_only
	count({j | some j in endpoint.processing_jurisdictions}) > 1
}

deny contains "model not approved" if not endpoint.model_id in profile.approved_models

deny contains "data class exceeds profile" if rank(input.data_class) > rank(profile.max_data_class)

# Commercial AWS may never stand in for an approved aws-eusc endpoint.
deny contains "cross-partition substitution" if {
	profile.permitted_domains == ["aws-eusc"]
	endpoint.domain != "aws-eusc"
}

allow if count(deny) == 0

# Agent tool authorization (Blueprint §9). Retrieved text can never satisfy these rules.
package sovereign.tools

import rego.v1

default allow := false

agent := data.agents[input.agent_id]

tool := data.tools[input.tool]

deny contains "unknown agent" if not agent

deny contains "agent suspended" if agent.suspended

deny contains "tool not in agent scope" if not input.tool in agent.allowed_tools

deny contains "target outside data scope" if not input.target in agent.data_scope

deny contains "wrong execution environment" if agent.environment != input.environment

deny contains msg if {
	some k, limit in tool.param_limits
	input.params[k] > limit
	msg := sprintf("parameter %s exceeds %v", [k, limit])
}

# High-impact actions need an approval bound to the exact action hash, unexpired.
deny contains "valid bound human approval required" if {
	tool.high_impact
	not valid_approval
}

valid_approval if {
	a := data.approvals[input.approval_id]
	a.action_hash == input.action_hash
	time.parse_rfc3339_ns(a.expires_at) > time.now_ns()
	not a.used
}

allow if count(deny) == 0

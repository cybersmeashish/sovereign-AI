from sovereign_ai.tool_gateway import AgentIdentity, ToolCall, ToolGateway, ToolSpec

def gw():
    g = ToolGateway([ToolSpec("read_ticket"), ToolSpec("scale_cluster", high_impact=True, param_limits={"nodes": 10})],
                    environment="vmware-private")
    g.register(AgentIdentity("ops-agent", "ops", {"read_ticket", "scale_cluster"}, {"prod-cluster", "itsm"}, "vmware-private"))
    return g

CALL = ToolCall("ops-agent", "alice", "scale_cluster", "prod-cluster", {"nodes": 5})


def test_high_impact_requires_bound_approval():
    g = gw()
    assert not g.authorize(CALL).allowed
    a = g.approve(CALL, "bob")
    other = ToolCall("ops-agent", "alice", "scale_cluster", "prod-cluster", {"nodes": 9})
    assert not g.authorize(other, a.approval_id).allowed      # different params
    assert g.authorize(CALL, a.approval_id).allowed
    assert not g.authorize(CALL, a.approval_id).allowed       # single use


def test_scope_limits_and_suspension():
    g = gw()
    assert not g.authorize(ToolCall("ops-agent", "a", "read_ticket", "hr-db", {})).allowed
    assert not g.authorize(ToolCall("ops-agent", "a", "scale_cluster", "prod-cluster", {"nodes": 50})).allowed
    assert g.start("j1", ToolCall("ops-agent", "a", "read_ticket", "itsm", {})).allowed
    assert g.suspend("ops-agent") == ["j1"]
    assert not g.authorize(ToolCall("ops-agent", "a", "read_ticket", "itsm", {})).allowed

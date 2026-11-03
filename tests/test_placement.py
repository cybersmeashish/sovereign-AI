from sovereign_ai import DeploymentDomain as D, Endpoint, NoEndpointBehavior, PlacementEngine, PlacementRequest, SovereigntyProfile

PROF = SovereigntyProfile(use_case_id="eu-assistant", owner="ops", risk_class="high",
                          permitted_domains=[D.AWS_EUSC], permitted_jurisdictions=["DE"],
                          max_data_class="confidential", approved_models=["m1"])
REQ = PlacementRequest("eu-assistant", "alice", True, "confidential", "m1", "v7")


def test_routes_to_eusc():
    eng = PlacementEngine([Endpoint("eusc-de", D.AWS_EUSC, "m1", ["DE"])])
    d = eng.decide(REQ, PROF)
    assert d.allowed and d.endpoint.endpoint_id == "eusc-de"


def test_commercial_not_silently_substituted():
    eng = PlacementEngine([Endpoint("eusc-de", D.AWS_EUSC, "m1", ["DE"], healthy=False),
                           Endpoint("com-fra", D.AWS_COMMERCIAL, "m1", ["DE"])])
    d = eng.decide(REQ, PROF)
    assert not d.allowed and d.action == "deny"


def test_geo_profile_spanning_jurisdictions_rejected():
    eng = PlacementEngine([Endpoint("eusc-geo", D.AWS_EUSC, "m1", ["DE", "FR"])])
    assert not eng.decide(REQ, PROF).allowed


def test_queue_behavior():
    eng = PlacementEngine([], NoEndpointBehavior.QUEUE)
    assert eng.decide(REQ, PROF).action == "queue"


def test_approved_fallback_only():
    eng = PlacementEngine([Endpoint("eusc-de", D.AWS_EUSC, "m1", ["DE"], healthy=False),
                           Endpoint("eusc-de-b", D.AWS_EUSC, "m1", ["DE"], approved_fallback_for=["eu-assistant"])],
                          NoEndpointBehavior.FALLBACK)
    assert eng.decide(REQ, PROF).endpoint.endpoint_id == "eusc-de-b"


def test_data_class_and_entitlement():
    eng = PlacementEngine([Endpoint("eusc-de", D.AWS_EUSC, "m1", ["DE"])])
    assert not eng.decide(PlacementRequest("eu-assistant", "a", True, "restricted", "m1", "v"), PROF).allowed
    assert not eng.decide(PlacementRequest("eu-assistant", "a", False, "internal", "m1", "v"), PROF).allowed

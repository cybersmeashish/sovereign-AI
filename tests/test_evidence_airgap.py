from sovereign_ai.airgap import build_bundle, quarantine_and_verify
from sovereign_ai.evidence import EvidenceLog
from sovereign_ai.signing import HMACSigner

S = HMACSigner(b"site")


def test_evidence_chain_and_minimised_export():
    log = EvidenceLog("hpe-disconnected")
    log.append("placement", {"use_case": "x", "prompt": "secret", "allowed": True})
    log.append("suspend", {"agent": "a1"})
    assert log.verify()
    rep = log.export(["use_case", "allowed", "agent"], "v3", S)
    assert "prompt" not in rep["records"][0]["data"] and rep["policy_version"] == "v3"
    log.records[0].data["allowed"] = False
    assert not log.verify()


def test_airgap_bundle_roundtrip_and_tamper(tmp_path):
    src = tmp_path / "src"; src.mkdir(); (src / "model.safetensors").write_bytes(b"weights")
    out = tmp_path / "b.tgz"
    build_bundle(src, out, S, "model-update", "custodian-1")
    assert quarantine_and_verify(out, tmp_path / "q1", S) == []
    assert quarantine_and_verify(out, tmp_path / "q2", HMACSigner(b"wrong")) == ["bundle signature invalid"]

from datetime import datetime, timedelta, timezone
from sovereign_ai.domains import DeploymentDomain as D
from sovereign_ai.manifest import REQUIRED_COMPONENTS, RELEASE_GATES, ReleaseManifest, verify_manifest
from sovereign_ai.signing import HMACSigner, sha256_hex

S = HMACSigner(b"rel")


def make(tmp_path, exp_days=7):
    comps = {}
    for c in REQUIRED_COMPONENTS:
        p = tmp_path / f"{c}.bin"; p.write_bytes(c.encode())
        comps[c] = {"path": p.name, "sha256": sha256_hex(c.encode()), "version": "1"}
    return ReleaseManifest("assistant", "1.0.0", ["vmware-private"], comps, {g: "owner" for g in RELEASE_GATES},
                           (datetime.now(timezone.utc) + timedelta(days=exp_days)).isoformat()).sign(S)


def test_valid_release(tmp_path):
    assert verify_manifest(make(tmp_path), S, D.VMWARE_PRIVATE, tmp_path) == []


def test_rejections(tmp_path):
    m = make(tmp_path)
    (tmp_path / "model.bin").write_bytes(b"swapped")
    errs = verify_manifest(m, S, D.AWS_COMMERCIAL, tmp_path)
    assert any("digest" in e for e in errs) and any("destination" in e for e in errs)
    m2 = make(tmp_path, exp_days=-1)
    assert any("expired" in e for e in verify_manifest(m2, S, D.VMWARE_PRIVATE))
    m3 = make(tmp_path); m3.approvals["production_placement"] = ""
    assert verify_manifest(m3, S, D.VMWARE_PRIVATE)  # signature now invalid + gate missing

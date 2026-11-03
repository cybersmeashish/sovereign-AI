"""`sovai` command line."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .domains import DeploymentDomain
from .manifest import ReleaseManifest, verify_manifest
from .placement import Endpoint, NoEndpointBehavior, PlacementEngine, PlacementRequest
from .profile import SovereigntyProfile
from .signing import HMACSigner, canonical, sha256_hex


def _signer() -> HMACSigner:
    key = os.environ.get("SOVAI_SIGNING_KEY")
    if not key:
        sys.exit("SOVAI_SIGNING_KEY is not set (use KMS/HSM-backed signing in production)")
    return HMACSigner(key.encode(), os.environ.get("SOVAI_KEY_ID", "hmac-default"))


def cmd_place(a) -> int:
    prof = SovereigntyProfile.load(a.profile)
    eps = [Endpoint(e["endpoint_id"], DeploymentDomain(e["domain"]), e["model_id"],
                    tuple(e["processing_jurisdictions"]), e.get("healthy", True),
                    tuple(e.get("approved_fallback_for", ())))
           for e in json.loads(Path(a.endpoints).read_text())]
    req = PlacementRequest(prof.use_case_id, a.caller, True, a.data_class, a.model, a.policy_version)
    d = PlacementEngine(eps, NoEndpointBehavior(a.no_endpoint)).decide(req, prof)
    print(json.dumps({"allowed": d.allowed, "action": d.action,
                      "endpoint": d.endpoint.endpoint_id if d.endpoint else None,
                      "reasons": d.reasons, "policy_version": d.policy_version}, indent=2))
    return 0 if d.allowed else 2


def cmd_sign_manifest(a) -> int:
    m = ReleaseManifest.from_json(Path(a.manifest).read_text())
    root = Path(a.artifacts)
    for spec in m.components.values():
        spec["sha256"] = sha256_hex((root / spec["path"]).read_bytes())
    m.sign(_signer())
    Path(a.out or a.manifest).write_text(m.to_json())
    print(f"signed {m.application}@{m.release}")
    return 0


def cmd_verify_manifest(a) -> int:
    m = ReleaseManifest.from_json(Path(a.manifest).read_text())
    errs = verify_manifest(m, _signer(), DeploymentDomain(a.target), Path(a.artifacts) if a.artifacts else None)
    print(json.dumps({"release": f"{m.application}@{m.release}", "ok": not errs, "violations": errs}, indent=2))
    return 0 if not errs else 3


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sovai", description="Sovereign AI Stack control-plane CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("place", help="evaluate placement policy for a request")
    s.add_argument("--profile", required=True); s.add_argument("--endpoints", required=True)
    s.add_argument("--model", required=True); s.add_argument("--data-class", default="internal")
    s.add_argument("--caller", default="cli-user"); s.add_argument("--policy-version", default="local")
    s.add_argument("--no-endpoint", default="deny", choices=[x.value for x in NoEndpointBehavior])
    s.set_defaults(fn=cmd_place)
    s = sub.add_parser("sign-manifest", help="compute digests and sign a release manifest")
    s.add_argument("manifest"); s.add_argument("--artifacts", required=True); s.add_argument("--out")
    s.set_defaults(fn=cmd_sign_manifest)
    s = sub.add_parser("verify-manifest", help="verify a release before deployment")
    s.add_argument("manifest"); s.add_argument("--target", required=True,
                                               choices=[d.value for d in DeploymentDomain])
    s.add_argument("--artifacts"); s.set_defaults(fn=cmd_verify_manifest)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())

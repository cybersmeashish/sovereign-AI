#!/usr/bin/env python3
"""Build / verify / promote physical-transfer bundles for disconnected sites."""
import argparse, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sovereign_ai.airgap import build_bundle, promote, quarantine_and_verify  # noqa: E402
from sovereign_ai.signing import HMACSigner  # noqa: E402


def signer():
    key = os.environ.get("SOVAI_SIGNING_KEY") or sys.exit("SOVAI_SIGNING_KEY not set")
    return HMACSigner(key.encode(), os.environ.get("SOVAI_KEY_ID", "site-key"))


p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="cmd", required=True)
b = sub.add_parser("build"); b.add_argument("--src", required=True); b.add_argument("--out", required=True)
b.add_argument("--purpose", required=True); b.add_argument("--custodian", required=True)
v = sub.add_parser("verify"); v.add_argument("--bundle", required=True); v.add_argument("--quarantine", required=True)
pr = sub.add_parser("promote"); pr.add_argument("--quarantine", required=True); pr.add_argument("--repo", required=True)
a = p.parse_args()
if a.cmd == "build":
    print(build_bundle(Path(a.src), Path(a.out), signer(), a.purpose, a.custodian)["signature"])
elif a.cmd == "verify":
    errs = quarantine_and_verify(Path(a.bundle), Path(a.quarantine), signer())
    print("\n".join(errs) or "VERIFIED"); sys.exit(1 if errs else 0)
else:
    promote(Path(a.quarantine), Path(a.repo)); print("PROMOTED")

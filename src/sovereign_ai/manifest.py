"""Signed application release manifest binding all security-relevant
components (Sections 5, 10). Unsigned artifacts, unexpected digests and
unapproved destinations are rejected."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .domains import DeploymentDomain
from .signing import Signer, canonical, sha256_hex

REQUIRED_COMPONENTS = ("model", "embedding_model", "retrieval_config", "prompt_template",
                       "safety_policy", "tool_definitions", "evaluation_suite")


@dataclass
class ReleaseManifest:
    application: str
    release: str
    approved_domains: List[str]
    components: Dict[str, Dict[str, str]]        # name -> {"path","sha256","version"}
    approvals: Dict[str, str]                    # gate -> approver (Table 3)
    expires_at: str
    signature: Optional[str] = None
    key_id: Optional[str] = None

    def payload(self) -> bytes:
        d = asdict(self); d.pop("signature"); d.pop("key_id")
        return canonical(d)

    def sign(self, signer: Signer) -> "ReleaseManifest":
        self.signature, self.key_id = signer.sign(self.payload()), signer.key_id
        return self

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)

    @classmethod
    def from_json(cls, text: str) -> "ReleaseManifest":
        return cls(**json.loads(text))


RELEASE_GATES = ("data_eligibility", "model_eligibility", "application_readiness", "production_placement")


def verify_manifest(m: ReleaseManifest, signer: Signer, target: DeploymentDomain,
                    artifact_root: Optional[Path] = None, now: Optional[datetime] = None) -> List[str]:
    """Return a list of violations; empty list means the release may deploy."""
    now = now or datetime.now(timezone.utc)
    errs: List[str] = []
    if not m.signature or not signer.verify(m.payload(), m.signature):
        errs.append("manifest signature invalid or missing")
    if datetime.fromisoformat(m.expires_at.replace("Z", "+00:00")) <= now:
        errs.append("release authorization expired")
    if target.value not in m.approved_domains:
        errs.append(f"destination {target.value} not approved")
    for c in REQUIRED_COMPONENTS:
        if c not in m.components:
            errs.append(f"missing bound component: {c}")
    for g in RELEASE_GATES:
        if not m.approvals.get(g):
            errs.append(f"release gate not approved: {g}")
    if artifact_root is not None:
        for name, spec in m.components.items():
            p = Path(artifact_root) / spec["path"]
            if not p.exists():
                errs.append(f"artifact missing: {name}")
            elif sha256_hex(p.read_bytes()) != spec["sha256"]:
                errs.append(f"unexpected digest: {name}")
    return errs

"""Versioned, signed policy packages with validity, revocation and an
offline validity window for disconnected sites (Section 7)."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .signing import Signer, canonical


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


@dataclass
class PolicyBundle:
    bundle_id: str
    version: int
    valid_from: str
    valid_until: str
    min_runtime_version: str
    policies: Dict[str, str]                         # name -> rego / rule text
    revoked_versions: List[int] = field(default_factory=list)
    signature: Optional[str] = None
    key_id: Optional[str] = None

    def payload(self) -> bytes:
        d = asdict(self); d.pop("signature"); d.pop("key_id")
        return canonical(d)

    def sign(self, signer: Signer) -> "PolicyBundle":
        self.signature, self.key_id = signer.sign(self.payload()), signer.key_id
        return self


class BundleRejected(Exception):
    pass


class PolicyStore:
    """Holds the active bundle. A WAN outage never removes the active bundle;
    expiry is handled by the configured local procedure (fail-closed by default)."""

    def __init__(self, signer: Signer, fail_closed_on_expiry: bool = True) -> None:
        self.signer = signer
        self.active: Optional[PolicyBundle] = None
        self.revoked: set[int] = set()
        self.fail_closed_on_expiry = fail_closed_on_expiry

    def install(self, b: PolicyBundle, now: Optional[datetime] = None) -> None:
        now = now or datetime.now(timezone.utc)
        if not b.signature or not self.signer.verify(b.payload(), b.signature):
            raise BundleRejected("invalid signature")
        if b.version in self.revoked or b.version in b.revoked_versions:
            raise BundleRejected(f"version {b.version} revoked")
        if self.active and b.version <= self.active.version:
            raise BundleRejected("rollback/replay: version not newer than active")
        if not (_ts(b.valid_from) <= now < _ts(b.valid_until)):
            raise BundleRejected("bundle outside validity window")
        self.revoked.update(b.revoked_versions)
        self.active = b

    def enforceable(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now(timezone.utc)
        if self.active is None:
            return False
        if now >= _ts(self.active.valid_until):
            return not self.fail_closed_on_expiry
        return True

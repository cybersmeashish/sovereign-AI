"""Tamper-evident evidence log with minimised, freshness-stamped exports
(Sections 7, 11, 14)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from .signing import Signer, canonical, sha256_hex

GENESIS = "0" * 64


@dataclass
class EvidenceRecord:
    seq: int
    ts: str
    domain: str
    kind: str
    data: Dict[str, Any]
    prev_hash: str
    hash: str


class EvidenceLog:
    def __init__(self, domain: str) -> None:
        self.domain = domain
        self.records: List[EvidenceRecord] = []

    def append(self, kind: str, data: Dict[str, Any]) -> EvidenceRecord:
        prev = self.records[-1].hash if self.records else GENESIS
        seq = len(self.records)
        ts = datetime.now(timezone.utc).isoformat()
        body = {"seq": seq, "ts": ts, "domain": self.domain, "kind": kind, "data": data, "prev": prev}
        rec = EvidenceRecord(seq, ts, self.domain, kind, data, prev, sha256_hex(canonical(body)))
        self.records.append(rec)
        return rec

    def verify(self) -> bool:
        prev = GENESIS
        for r in self.records:
            body = {"seq": r.seq, "ts": r.ts, "domain": r.domain, "kind": r.kind, "data": r.data, "prev": prev}
            if r.prev_hash != prev or r.hash != sha256_hex(canonical(body)):
                return False
            prev = r.hash
        return True

    def export(self, allowed_fields: Iterable[str], policy_version: str, signer: Signer) -> Dict[str, Any]:
        """Export only fields permitted by the local disclosure policy, stamped
        with reporting time and policy version so receivers can judge freshness."""
        allowed = set(allowed_fields)
        items = [{"seq": r.seq, "ts": r.ts, "kind": r.kind,
                  "data": {k: v for k, v in r.data.items() if k in allowed}} for r in self.records]
        report = {"domain": self.domain, "reported_at": datetime.now(timezone.utc).isoformat(),
                  "policy_version": policy_version,
                  "head_hash": self.records[-1].hash if self.records else GENESIS, "records": items}
        report["signature"] = signer.sign(canonical(report))
        report["key_id"] = signer.key_id
        return report

    def dump(self) -> str:
        return "\n".join(json.dumps(asdict(r), sort_keys=True) for r in self.records)

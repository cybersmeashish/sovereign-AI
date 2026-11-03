"""Permission-aware retrieval (Section 8).

* entitlements are applied BEFORE content enters model context;
* access is re-checked when a citation is resolved;
* entitlement versions make stale grants detectable;
* retrieved text is wrapped as untrusted data and can never grant permissions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

INJECTION_PATTERNS = [
    r"ignore (all|any|previous) (instructions|rules)",
    r"you are now", r"system prompt", r"grant (me|yourself) (access|permission)",
    r"call the tool", r"send (this|the data) to", r"route (this|requests) to",
]


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str
    allowed_groups: frozenset
    classification: str = "internal"


class EntitlementStore:
    def __init__(self) -> None:
        self._groups: Dict[str, Set[str]] = {}
        self.version = 0

    def grant(self, user: str, group: str) -> None:
        self._groups.setdefault(user, set()).add(group); self.version += 1

    def revoke(self, user: str, group: str) -> None:
        self._groups.get(user, set()).discard(group); self.version += 1

    def groups(self, user: str) -> Set[str]:
        return set(self._groups.get(user, set()))


@dataclass
class RetrievedPassage:
    doc_id: str
    content: str
    entitlement_version: int
    injection_suspected: bool

    def as_context(self) -> str:
        flag = " injection-suspected=\"true\"" if self.injection_suspected else ""
        return (f"<untrusted_document id=\"{self.doc_id}\"{flag}>\n{self.content}\n</untrusted_document>")


def suspicious(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in INJECTION_PATTERNS)


class PermissionAwareRetriever:
    def __init__(self, docs: List[Document], entitlements: EntitlementStore) -> None:
        self.docs = {d.doc_id: d for d in docs}
        self.ent = entitlements

    def _can_read(self, user: str, d: Document) -> bool:
        return bool(self.ent.groups(user) & set(d.allowed_groups))

    def retrieve(self, user: str, query: str, k: int = 5) -> List[RetrievedPassage]:
        terms = set(query.lower().split())
        scored: List[Tuple[int, Document]] = []
        for d in self.docs.values():
            if not self._can_read(user, d):      # filter BEFORE ranking/context
                continue
            score = len(terms & set(d.text.lower().split()))
            if score:
                scored.append((score, d))
        scored.sort(key=lambda x: -x[0])
        return [RetrievedPassage(d.doc_id, d.text, self.ent.version, suspicious(d.text)) for _, d in scored[:k]]

    def resolve_citation(self, user: str, passage: RetrievedPassage) -> Document:
        d = self.docs[passage.doc_id]
        if not self._can_read(user, d):
            raise PermissionError(f"access to {d.doc_id} no longer permitted")
        return d

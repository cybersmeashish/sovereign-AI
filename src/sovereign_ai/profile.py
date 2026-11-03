"""Sovereignty profile: the testable requirements recorded per AI use case (Section 1)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .domains import DeploymentDomain

DATA_CLASSES = ("public", "internal", "confidential", "restricted")


@dataclass(frozen=True)
class SovereigntyProfile:
    use_case_id: str
    owner: str
    risk_class: str
    permitted_domains: List[DeploymentDomain]
    permitted_jurisdictions: List[str]
    max_data_class: str = "internal"
    key_custody: str = "customer"            # customer | provider | hsm-local
    administrator_eligibility: List[str] = field(default_factory=list)
    allowed_egress: List[str] = field(default_factory=list)
    autonomy_hours: int = 0                   # hours the service must run without external deps
    approved_models: List[str] = field(default_factory=list)
    country_only: bool = False
    review_date: Optional[str] = None

    def __post_init__(self) -> None:
        if self.max_data_class not in DATA_CLASSES:
            raise ValueError(f"unknown data class {self.max_data_class!r}")
        if not self.permitted_domains:
            raise ValueError("a profile must permit at least one deployment domain")

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SovereigntyProfile":
        d = dict(d)
        d["permitted_domains"] = [DeploymentDomain(x) for x in d["permitted_domains"]]
        return cls(**d)

    @classmethod
    def load(cls, path: str | Path) -> "SovereigntyProfile":
        text = Path(path).read_text()
        if str(path).endswith((".yaml", ".yml")):
            import yaml  # optional dependency
            return cls.from_dict(yaml.safe_load(text))
        return cls.from_dict(json.loads(text))

    def permits_data_class(self, data_class: str) -> bool:
        return DATA_CLASSES.index(data_class) <= DATA_CLASSES.index(self.max_data_class)

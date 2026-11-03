"""Placement policy evaluated before processing begins (Sections 3, 11).

The engine never silently substitutes an endpoint: if no eligible endpoint
exists the configured behavior (queue / deny / approved fallback) applies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Sequence

from .domains import DeploymentDomain
from .profile import SovereigntyProfile


class NoEndpointBehavior(str, Enum):
    DENY = "deny"
    QUEUE = "queue"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class Endpoint:
    endpoint_id: str
    domain: DeploymentDomain
    model_id: str
    # Every jurisdiction the request MAY be processed in (e.g. all Regions
    # of a geographic cross-Region inference profile), not just the home Region.
    processing_jurisdictions: Sequence[str]
    healthy: bool = True
    approved_fallback_for: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class PlacementRequest:
    use_case_id: str
    caller: str
    caller_entitled: bool
    data_class: str
    model_id: str
    policy_version: str


@dataclass(frozen=True)
class PlacementDecision:
    allowed: bool
    action: str                      # route | deny | queue
    endpoint: Optional[Endpoint]
    reasons: List[str]
    policy_version: str


class PlacementEngine:
    def __init__(self, endpoints: Sequence[Endpoint],
                 no_endpoint: NoEndpointBehavior = NoEndpointBehavior.DENY) -> None:
        self.endpoints = list(endpoints)
        self.no_endpoint = no_endpoint

    def _eligible(self, ep: Endpoint, req: PlacementRequest, prof: SovereigntyProfile, why: List[str]) -> bool:
        if ep.domain not in prof.permitted_domains:
            why.append(f"{ep.endpoint_id}: domain {ep.domain.value} not permitted"); return False
        if ep.model_id != req.model_id or (prof.approved_models and ep.model_id not in prof.approved_models):
            why.append(f"{ep.endpoint_id}: model {ep.model_id} not approved for request"); return False
        outside = set(ep.processing_jurisdictions) - set(prof.permitted_jurisdictions)
        if outside:
            why.append(f"{ep.endpoint_id}: may process in unapproved jurisdictions {sorted(outside)}"); return False
        if prof.country_only and len(set(ep.processing_jurisdictions)) > 1:
            why.append(f"{ep.endpoint_id}: multi-jurisdiction profile violates country-only rule"); return False
        if not ep.healthy:
            why.append(f"{ep.endpoint_id}: unhealthy"); return False
        return True

    def decide(self, req: PlacementRequest, prof: SovereigntyProfile) -> PlacementDecision:
        why: List[str] = []
        if req.use_case_id != prof.use_case_id:
            return PlacementDecision(False, "deny", None, ["profile does not match use case"], req.policy_version)
        if not req.caller_entitled:
            return PlacementDecision(False, "deny", None, ["caller not entitled to use case"], req.policy_version)
        if not prof.permits_data_class(req.data_class):
            return PlacementDecision(False, "deny", None,
                                     [f"data class {req.data_class} exceeds profile maximum {prof.max_data_class}"],
                                     req.policy_version)
        primary = [ep for ep in self.endpoints if not ep.approved_fallback_for]
        for ep in primary:
            if self._eligible(ep, req, prof, why):
                return PlacementDecision(True, "route", ep, why + [f"routed to {ep.endpoint_id}"], req.policy_version)
        if self.no_endpoint is NoEndpointBehavior.FALLBACK:
            for ep in self.endpoints:
                if req.use_case_id in ep.approved_fallback_for and self._eligible(ep, req, prof, why):
                    return PlacementDecision(True, "route", ep, why + [f"approved fallback {ep.endpoint_id}"], req.policy_version)
        action = "queue" if self.no_endpoint is NoEndpointBehavior.QUEUE else "deny"
        return PlacementDecision(False, action, None, why + ["no eligible endpoint"], req.policy_version)

"""Sovereign AI Stack - reference control plane.

Implements the enforceable controls described in the Sovereign AI Stack
Enterprise Blueprint: placement decisions, signed policy bundles, signed
release manifests, permission-aware retrieval, agent tool authorization
with bound human approvals, and tamper-evident evidence capture.
"""
from .domains import DeploymentDomain
from .profile import SovereigntyProfile
from .placement import Endpoint, PlacementRequest, PlacementDecision, PlacementEngine, NoEndpointBehavior

__version__ = "0.1.0"
__all__ = [
    "DeploymentDomain", "SovereigntyProfile", "Endpoint", "PlacementRequest",
    "PlacementDecision", "PlacementEngine", "NoEndpointBehavior", "__version__",
]

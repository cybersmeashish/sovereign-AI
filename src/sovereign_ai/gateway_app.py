"""Minimal local AI gateway (FastAPI) applying placement before inference.

Run:  uvicorn sovereign_ai.gateway_app:app --port 8080
Model backends are OpenAI-compatible endpoints (e.g. vLLM on VMware/HPE,
or a Bedrock access gateway) configured in SOVAI_ENDPOINTS (JSON file)."""
from __future__ import annotations

import json
import os
from pathlib import Path

from .domains import DeploymentDomain
from .evidence import EvidenceLog
from .placement import Endpoint, NoEndpointBehavior, PlacementEngine, PlacementRequest
from .profile import SovereigntyProfile

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    raise SystemExit("install extras: pip install 'sovereign-ai[gateway]'")

DOMAIN = os.environ.get("SOVAI_DOMAIN", "vmware-private")
PROFILES_DIR = Path(os.environ.get("SOVAI_PROFILES", "examples/profiles"))
ENDPOINTS = Path(os.environ.get("SOVAI_ENDPOINTS", "examples/endpoints.json"))

app = FastAPI(title="Sovereign AI Gateway", version="0.1.0")
evidence = EvidenceLog(DOMAIN)


def _engine() -> PlacementEngine:
    eps = [Endpoint(e["endpoint_id"], DeploymentDomain(e["domain"]), e["model_id"],
                    tuple(e["processing_jurisdictions"]), e.get("healthy", True),
                    tuple(e.get("approved_fallback_for", ()))) for e in json.loads(ENDPOINTS.read_text())]
    return PlacementEngine(eps, NoEndpointBehavior(os.environ.get("SOVAI_NO_ENDPOINT", "deny")))


class InferenceIn(BaseModel):
    use_case_id: str
    caller: str
    model_id: str
    data_class: str = "internal"
    prompt: str


@app.get("/healthz")
def healthz():
    return {"status": "ok", "domain": DOMAIN, "evidence_chain_valid": evidence.verify()}


@app.post("/v1/placement")
def placement(body: InferenceIn):
    path = PROFILES_DIR / f"{body.use_case_id}.json"
    if not path.exists():
        raise HTTPException(404, "no sovereignty profile for use case")
    prof = SovereigntyProfile.load(path)
    d = _engine().decide(PlacementRequest(body.use_case_id, body.caller, True, body.data_class,
                                          body.model_id, os.environ.get("SOVAI_POLICY_VERSION", "local")), prof)
    evidence.append("placement", {"use_case": body.use_case_id, "caller": body.caller, "allowed": d.allowed,
                                  "endpoint": d.endpoint.endpoint_id if d.endpoint else None,
                                  "policy_version": d.policy_version})  # prompt content intentionally NOT logged
    if not d.allowed:
        raise HTTPException(403 if d.action == "deny" else 503, {"action": d.action, "reasons": d.reasons})
    return {"endpoint": d.endpoint.endpoint_id, "reasons": d.reasons}

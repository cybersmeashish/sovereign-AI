"""Deterministic agent tool authorization (Section 9).

Each agent has its own identity and scope. High-impact actions need a human
approval bound to the exact action hash with an expiry. A model claiming that
approval exists has no effect. Suspension revokes the agent immediately.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set

from .signing import canonical, sha256_hex


@dataclass(frozen=True)
class ToolSpec:
    name: str
    high_impact: bool = False
    max_data_class: str = "internal"
    param_limits: Dict[str, Any] = field(default_factory=dict)   # e.g. {"amount": 1000}


@dataclass
class AgentIdentity:
    agent_id: str
    purpose: str
    allowed_tools: Set[str]
    data_scope: Set[str]
    environment: str
    suspended: bool = False


@dataclass(frozen=True)
class ToolCall:
    agent_id: str
    caller: str
    tool: str
    target: str
    params: Dict[str, Any]
    data_class: str = "internal"

    def action_hash(self) -> str:
        return sha256_hex(canonical({"agent": self.agent_id, "caller": self.caller, "tool": self.tool,
                                     "target": self.target, "params": self.params, "dc": self.data_class}))


@dataclass
class Approval:
    approval_id: str
    action_hash: str
    approver: str
    expires_at: datetime
    agent_id: str = ""
    used: bool = False


@dataclass
class Decision:
    allowed: bool
    reason: str


_DC = ["public", "internal", "confidential", "restricted"]


class ToolGateway:
    def __init__(self, tools: List[ToolSpec], environment: str) -> None:
        self.tools = {t.name: t for t in tools}
        self.environment = environment
        self.agents: Dict[str, AgentIdentity] = {}
        self.approvals: Dict[str, Approval] = {}
        self.in_flight: Dict[str, ToolCall] = {}
        self.audit: List[Dict[str, Any]] = []

    def register(self, agent: AgentIdentity) -> None:
        self.agents[agent.agent_id] = agent

    def approve(self, call: ToolCall, approver: str, ttl_minutes: int = 15) -> Approval:
        a = Approval(secrets.token_hex(8), call.action_hash(), approver,
                     datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes), call.agent_id)
        self.approvals[a.approval_id] = a
        return a

    def authorize(self, call: ToolCall, approval_id: Optional[str] = None) -> Decision:
        d = self._authorize(call, approval_id)
        self.audit.append({"ts": datetime.now(timezone.utc).isoformat(), "agent": call.agent_id,
                           "tool": call.tool, "action": call.action_hash(), "allowed": d.allowed, "reason": d.reason})
        return d

    def _authorize(self, call: ToolCall, approval_id: Optional[str]) -> Decision:
        agent = self.agents.get(call.agent_id)
        if agent is None:
            return Decision(False, "unknown agent identity")
        if agent.suspended:
            return Decision(False, "agent suspended")
        if agent.environment != self.environment:
            return Decision(False, "agent not approved for this execution environment")
        spec = self.tools.get(call.tool)
        if spec is None or call.tool not in agent.allowed_tools:
            return Decision(False, "tool not permitted for agent")
        if call.target not in agent.data_scope:
            return Decision(False, "target outside agent data scope")
        if _DC.index(call.data_class) > _DC.index(spec.max_data_class):
            return Decision(False, "data classification exceeds tool limit")
        for k, limit in spec.param_limits.items():
            v = call.params.get(k)
            if isinstance(v, (int, float)) and v > limit:
                return Decision(False, f"parameter {k} exceeds limit {limit}")
        if spec.high_impact:
            a = self.approvals.get(approval_id or "")
            if a is None:
                return Decision(False, "human approval required")
            if a.used:
                return Decision(False, "approval already used")
            if a.expires_at <= datetime.now(timezone.utc):
                return Decision(False, "approval expired")
            if a.action_hash != call.action_hash():
                return Decision(False, "approval not bound to this exact action")
            a.used = True
        return Decision(True, "authorized")

    def start(self, job_id: str, call: ToolCall, approval_id: Optional[str] = None) -> Decision:
        d = self.authorize(call, approval_id)
        if d.allowed:
            self.in_flight[job_id] = call
        return d

    def suspend(self, agent_id: str) -> List[str]:
        """Kill switch: disable identity, revoke approvals, return in-flight jobs to cancel."""
        agent = self.agents[agent_id]
        agent.suspended = True
        agent.allowed_tools = set()
        for a in self.approvals.values():
            if a.agent_id == agent_id:
                a.used = True
        jobs = [j for j, c in self.in_flight.items() if c.agent_id == agent_id]
        for j in jobs:
            self.in_flight.pop(j)
        self.audit.append({"ts": datetime.now(timezone.utc).isoformat(), "agent": agent_id,
                           "event": "suspended", "cancelled_jobs": jobs})
        return jobs

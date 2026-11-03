# Reference architecture

![Five deployment domains](images/figure-1-deployment-domains.png)

## Domains and boundaries

```mermaid
flowchart LR
  subgraph GOV[Enterprise AI Governance Authority]
    INV[Use-case inventory\nrisk classes, owners]
    POL[Signed policy packages]
    EVR[Evidence repository]
  end
  subgraph AWS[aws partition - commercial]
    A1[IAM / KMS / CloudTrail] --> A2[AI gateway] --> A3[Bedrock + Guardrails\nSageMaker AI]
  end
  subgraph EUSC[aws-eusc partition - EU sovereign]
    E1[EU IAM / KMS] --> E2[AI gateway] --> E3[Bedrock / SageMaker\nin EUSC Region]
  end
  subgraph VMW[VMware Cloud Foundation]
    V1[Local IdP / keys] --> V2[AI gateway + OPA] --> V3[vLLM on VKS\nHarbor model store]
  end
  subgraph HPES[HPE GreenLake sovereign]
    H1[Local IdP / HSM] --> H2[AI gateway + OPA] --> H3[HPE Private Cloud AI]
  end
  subgraph HPED[HPE disconnected - air gap]
    D1[Local IdP / HSM / NTP / PKI] --> D2[AI gateway + OPA] --> D3[Private Cloud AI\nHarbor mirror]
  end
  POL -->|signed bundle| AWS & EUSC & VMW & HPES
  POL -. physical media .-> HPED
  AWS & EUSC & VMW & HPES -->|minimised evidence| EVR
  HPED -. physical media .-> EVR
```

## Request path inside any domain

```mermaid
sequenceDiagram
  participant U as Caller / Agent
  participant G as AI Gateway
  participant P as Placement + OPA
  participant R as Permission-aware retrieval
  participant M as Approved model endpoint
  participant T as Tool gateway
  participant E as Evidence log
  U->>G: request (identity, use case, data class)
  G->>P: placement decision (profile, policy version)
  P-->>G: route / deny / queue
  G->>R: retrieve with caller entitlements
  R-->>G: authorised passages (wrapped untrusted)
  G->>M: prompt + passages
  M-->>G: response / tool proposal
  G->>T: tool call (agent id, params, approval id)
  T-->>G: authorised / denied
  G->>E: decision metadata (no prompt content)
```

## Module map

| Blueprint control | Code | Policy |
|---|---|---|
| Sovereignty profile (§1) | `sovereign_ai/profile.py`, `schemas/sovereignty-profile.schema.json` | — |
| Placement / inference routing (§3, §11) | `sovereign_ai/placement.py` | `policies/placement.rego` |
| Signed, versioned policy with offline validity (§7) | `sovereign_ai/policy_bundle.py` | OPA signed bundles |
| Permission-aware retrieval, injection handling (§8) | `sovereign_ai/retrieval.py` | — |
| Agent identity, bound approvals, suspension (§9) | `sovereign_ai/tool_gateway.py` | `policies/tool_authz.rego` |
| Signed release manifests and gates (§10) | `sovereign_ai/manifest.py` | `policies/release.rego` |
| Air-gap import/export (§12) | `sovereign_ai/airgap.py`, `scripts/airgap_bundle.py` | — |
| Evidence & disclosure-minimised export (§7, §14) | `sovereign_ai/evidence.py` | — |

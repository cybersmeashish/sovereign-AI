# Hybrid cloud data flows (Blueprint §11, Table 4)

| Flow | Default behavior | Required control | Implemented by |
|---|---|---|---|
| Prompt → model | Process within approved domain | Placement + identity decision | `PlacementEngine`, `placement.rego` |
| Retrieval from sources | Only authorised content | Entitlement enforcement | `PermissionAwareRetriever` |
| Model release → other domain | Separate promotion workflow | License, provenance, signed manifest | `ReleaseManifest`, `release.rego` |
| Policy update → connected domain | Authorised channels | Signature, version, validity | `PolicyStore`, OPA bundles |
| Update → air-gapped site | Physical media | Quarantine, inspection, local verification | `airgap.py` |
| Evidence → enterprise authority | Approved metadata / summaries | Disclosure review, minimisation, integrity | `EvidenceLog.export` |

Transfers between `aws` and `aws-eusc` partitions are explicit boundary crossings: approve
identity, transport, destination and disclosure per transfer, and create independent
destination resources and release approvals.

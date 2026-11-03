# Production acceptance evidence (Blueprint §14)

Each criterion maps to an automated check in this repo plus the evidence that must be produced
against the **actual** platform configuration before release.

| # | Criterion | Automated check | Platform evidence to attach |
|---|---|---|---|
| 1 | No routing to unapproved region/model/service/support endpoint | `tests/test_placement.py`, `policies/placement_test.rego` | SCP / VPC-endpoint policy test, egress deny logs |
| 2 | Restricted docs not retrievable; permission changes apply within interval | `tests/test_retrieval.py` | Entitlement-sync latency measurement |
| 3 | Retrieved instructions cannot authorise tools or alter boundary | `tests/test_retrieval.py`, `tests/test_tool_gateway.py` | Red-team injection report |
| 4 | High-impact action needs approval bound to exact parameters | `tests/test_tool_gateway.py` | Approval audit records |
| 5 | Invalid signature / unexpected artifact / expired authorization rejected | `tests/test_manifest.py`, `tests/test_evidence_airgap.py` | Deploy pipeline rejection logs |
| 6 | Agent suspension blocks new and in-progress execution | `tests/test_tool_gateway.py` | Platform cancellation drill |
| 7 | Disconnected site runs inference, retrieval, enforcement, monitoring, recovery offline | `infra/vmware-private/networkpolicy.yaml` + offline drill | Air-gap drill report |
| 8 | EUSC app meets continuity targets without specified external dependencies | Dependency-removal test plan | Independence test report |
| 9 | Commercial AWS cannot silently substitute for EUSC endpoint/identity | `test_commercial_not_silently_substituted`, `partition_guard` | Partition check output |
| 10 | Backup restore preserves keys, provenance, policy state, placement | Restore runbook | Restore test record |
| 11 | Exported evidence meets disclosure rules, carries time + policy version | `tests/test_evidence_airgap.py` | Disclosure review sign-off |
| 12 | Failover and capacity meet objectives | Load-test harness | Load / failover report |

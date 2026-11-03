# Operating model and responsibilities (Blueprint §13)

| Decision | Governance authority | Data owner | Model owner | App team | Platform ops | SecOps | Site custodian |
|---|---|---|---|---|---|---|---|
| Approve use case & sovereignty profile | **A** | C | C | R | C | C | I |
| Approve exception | **A** | C | C | R | C | C | I |
| Data eligibility gate | C | **A/R** | I | C | I | C | I |
| Model eligibility gate | C | I | **A/R** | C | C | C | I |
| Application readiness gate | C | C | C | **R** | I | **A** | I |
| Production placement gate | **A** | I | I | C | **R** | C | C |
| Revoke access / suspend agent | I | C | C | C | R | **A/R** | R (offline sites) |
| Authorise evidence export | C | C | I | I | I | C | **A/R** |
| Activate recovery | I | I | I | C | **R** | C | **A** (offline) |

R = responsible, A = accountable, C = consulted, I = informed.

## Deployment stages (Table 5)

| Stage | Scope | Exit criterion |
|---|---|---|
| 1. Establish boundaries | Inventory use cases, define sovereignty profiles | Owners and permitted flows approved |
| 2. Prove the application | AWS or VMware pilot in an eligible boundary | Authorization, evaluation, recovery tests pass |
| 3. Sovereign operations | AWS EUSC or selected HPE environment | Partition, operator, key, support boundaries verified |
| 4. Disconnected operation | Selected air-gapped configuration | Workflows function with external access blocked |
| 5. Expand production | More workloads, sites, governance reporting | Capacity, ownership, acceptance evidence approved |

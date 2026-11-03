# Building a Sovereign AI Stack

*Enterprise AI governance across AWS VMware and HPE GreenLake*

Large enterprises need an AI architecture that can accommodate different requirements for data location, operational control and network isolation. The proposed blueprint separates AWS commercial public cloud from AWS European Sovereign Cloud, uses VMware for enterprise private cloud, and uses HPE GreenLake offerings for sovereign and disconnected deployments. Hybrid operations coordinate approved workflows across these boundaries.

The recommendation is to establish one enterprise governance model and enforce it within every deployment boundary. Each environment needs the controls required for its workloads: identity, data authorization, approved models, runtime protection, evaluation, incident response and audit evidence. A disconnected site must operate these controls locally.

This article describes the architecture, platform responsibilities and production acceptance criteria. Product capabilities inform the design; deployment policies, integration choices and operating requirements below are proposed enterprise controls.

![Shared enterprise AI governance across AWS commercial public cloud, AWS European Sovereign Cloud in its separate aws-eusc partition, VMware private cloud, HPE sovereign cloud, and HPE disconnected deployments. Each domain has identity, data authorization, runtime controls, approved models, agents, evaluation and evidence. Disconnected sites exchange approved policy and evidence through verified physical transfer.](images/figure-1-deployment-domains.png)

Figure 1 Five deployment domains share governance standards and enforce their own AI operating boundaries. AWS European Sovereign Cloud has a separate partition. Dashed paths represent approved physical imports and exports for the HPE disconnected domain.

# 1 Define sovereignty before selecting the runtime

Start with an explicit sovereignty profile for each AI use case. Record where processing may occur, who may administer the system, which parties control encryption keys, what information may leave the boundary and how long the service must function without external dependencies. HPE describes sovereign design in terms of operational, data and technology control; the architecture must translate those dimensions into testable requirements. [R8]

The profile should cover source data, prompts, retrieved passages, embeddings, model weights, fine-tuning datasets, outputs, traces, backups and evaluation records. It should also address remote support access, software activation, update services and model-provider terms. Storage location alone does not resolve every requirement.

Keep jurisdiction, operational autonomy and connectivity as separate requirements. AWS European Sovereign Cloud is designed for EU operational autonomy while providing connected cloud services. Its reported independence exercise used public-internet rerouting when the AWS Global Network backbone was disabled. A strict air gap has no external network connection and uses a separate operating model. [R23] [R24] [R11]

# 2 Establish five deployment domains

Hybrid cloud is the operating relationship between the domains below. It is not an additional location where sensitive data can be placed without review.

Table 1 AI deployment domains

| **Deployment domain** | **Platform basis** | **Suitable workload pattern** | **Required placement decision** |
|---|---|---|---|
| AWS commercial public cloud | Approved commercial AWS Regions and accounts | Managed AI services and elastic processing of approved data | Approve the service, model, processing destinations and provider terms |
| AWS European Sovereign Cloud | Separate aws-eusc partition and EU landing zone | Eligible AI services for workloads requiring EU operational and data controls | Approve partition resources, available services, processing locations and provider terms |
| VMware private cloud | VMware Cloud Foundation and supported Private AI services | Internal assistants and AI services near enterprise data | Approve local dependencies, GPU capacity, support access and administrator roles |
| HPE sovereign environment | HPE GreenLake private-cloud and AI offerings within an approved jurisdiction | AI workloads requiring defined local ownership and operational control | Establish jurisdiction, key custody, operator eligibility and permitted connections |
| HPE disconnected environment | Specifically supported air-gapped private-cloud and AI configurations | Isolated inference, retrieval and approved model maintenance | Prove local operation and approve separate physical import and export procedures |

AWS documents commercial-cloud routing considerations and a separate European Sovereign Cloud architecture. VMware documents Private AI services, and HPE identifies sovereign and air-gapped portfolio options. These foundations are eligible only where the workload's sovereignty profile is satisfied. [R2] [R25] [R7] [R8] [R9]

# 3 Build the AWS commercial public cloud stack

Use an AWS landing zone with separate accounts for AI development, production, data and security administration. Apply organization policies and service permissions to the approved processing boundary. AWS's Security Reference Architecture for generative AI provides the basis for separating workload, data and security responsibilities. [R1]

For managed model access, use Amazon Bedrock where the selected model and invocation mode satisfy the placement policy. Use Amazon SageMaker AI for suitable custom model development and deployment. SageMaker Model Registry, Model Cards and Model Dashboard provide model-management and governance capabilities; connect their records to the enterprise use-case inventory and approval process. [R6] [R21]

Use IAM roles for workload identity, scoped data access, appropriate AWS KMS key policies and CloudTrail activity records. Protect application traces under a separate retention and access policy. For agent workloads, evaluate Bedrock AgentCore Identity, Gateway and Policy as AWS implementations of identity, tool access and action-policy controls. Check availability in the approved Region before selecting them. [R1] [R3]

Treat inference routing as a governance decision. Bedrock distinguishes geographic and global cross-Region inference profiles, and its policies can constrain allowed profiles and destinations. A geographic profile may still span multiple jurisdictions. A country-only requirement needs an eligible profile or in-Region processing. Blocking a destination required by a geographic profile can make that profile unavailable; approve the actual destination set and failure behavior. [R2] [R20]

Use private service connectivity where supported, with appropriate identity and network controls. Bedrock PrivateLink provides private connectivity to the service; service-location and provider requirements still need their own approval. Review model-specific data-processing and retention conditions when approving a model. [R5] [R3]

Apply Bedrock Guardrails to eligible AWS flows, alongside application authorization and tool permissions. Its independent ApplyGuardrail API also accepts content from applications using other models. Calling that API from a private or sovereign environment sends the submitted content to an AWS service, so the transfer must satisfy that environment's placement policy. Check guardrail processing locations separately: AWS also supports cross-Region guardrail profiles. [R4] [R22]

# 4 Build the AWS European Sovereign Cloud stack

AWS's design goals cover EU data residency, operational autonomy, technical safeguards, access to AWS cloud capabilities, and governance under an EU legal framework. Its infrastructure is located within the EU, and AWS states that AWS-created customer metadata remains there. Infrastructure operations and support use qualified EU residents located in the EU, with a stated transition toward EU-citizen staffing. Record these provider commitments separately from the enterprise's own user and administrator eligibility rules. [R23]

Build a dedicated landing zone in the `aws-eusc` partition. Use separate accounts, organizations, IAM resources, endpoints and automation. AWS documents isolation from commercial-partition resources and limitations including cross-partition role assumption and consolidated billing. Create a partition-specific approval record for services, models, security controls and support dependencies. [R25]

AWS's launch announcement includes Amazon Bedrock and Amazon SageMaker among the AI services. Verify the particular model, feature, capacity and endpoint available in the selected European Sovereign Cloud Region. Service names shared with commercial AWS do not establish feature or model parity. [R26]

AWS's report published on November 1, 2026 describes an exercise performed on October 24. AWS disabled the Global Network backbone connections and its controlled operational-data transfer system for several hours. Traffic rerouted securely over the public internet; AWS reports that customer availability, data-center operations and security monitoring were unaffected. This is provider-reported evidence of the tested conditions. It does not establish every application's independence or an unlimited isolation duration. [R24]

For the proposed AI architecture, keep identity, data access, keys, retrieval, inference, guardrail processing, evidence and recovery within the approved EU boundary. Give the EU operating team access to its approved policies and incident procedures without requiring an external governance console. Test enterprise dependencies separately, including federated identity, source systems, package repositories and external model APIs.

# 5 Build the VMware private cloud stack

Use VMware Cloud Foundation as the private-cloud infrastructure foundation, with the supported AI services and GPU configuration selected for the enterprise. VMware documents Private AI services for model storage, model endpoints and data indexing and retrieval workflows. These capabilities provide a basis for running AI services close to internal datasets. [R7]

The documented implementation uses a Harbor-based model store and model endpoints supported by VMware Kubernetes Service, with inference engines such as vLLM. Select supported engines, model formats and GPU allocations for the chosen release. [R7]

Implement a private AI service path consisting of application authentication, a local AI gateway, data authorization, retrieval, model execution and protected observability. The gateway should select only endpoints approved for the caller and the use case. Enforce administrative separation between infrastructure operators, data owners, model owners and application teams.

Maintain a local model repository and signed deployment manifests. Bind the model version to the embedding model, retrieval configuration, prompt template, safety policy and permitted tools. This binding allows the enterprise to reproduce an approved application and roll back a release coherently.

Validate the complete dependency set for isolated operation: container images, model downloads, certificates, name resolution, time services, telemetry, support and licensing workflows. Demonstrate the selected product configuration with external access blocked before approving it for an isolated workload. Repeat this validation when releases or dependencies change.

# 6 Use HPE GreenLake for sovereign and disconnected domains

Create the sovereign environment around a defined legal and operating boundary. HPE's sovereign-cloud materials describe control of data, operations and technology, while its private-cloud portfolio includes AI and air-gapped configurations. Select the exact offering and service arrangement that matches the required boundary. [R8] [R9]

Use HPE Private Cloud AI as an AI workload platform. Select Private Cloud Enterprise or another supported private-cloud offering where the requirement is infrastructure and cloud management. Treat these as deployment choices with their own supported configurations. Define the operating organization and service personnel permitted for each offering, and verify interoperability, support conditions and licensing during procurement. [R8]

For the disconnected domain, select an explicitly supported air-gapped configuration. HPE describes air-gapped options for Private Cloud Enterprise and Private Cloud AI. Its current portfolio also lists HPE Private Cloud PC7000a for regulated environments. Offline acceptance must assess the exact configuration, its operating duties and the selected application dependencies. [R8] [R9]

Provide local identity, keys, model storage, artifact mirrors, policy enforcement, evaluation, logging and recovery. HPE documents Harbor as a locally hosted container registry within Private Cloud AI, providing one option for internal image distribution. [R10] Use approved physical transfer workflows for updates and reports. Treat HPE, VMware and AWS as defined responsibility boundaries: any combination of their components needs its own supported integration and operating model.

# 7 Make governance enforceable at every layer

The enterprise AI governance authority should maintain the use-case inventory, risk classifications, ownership, approval rules and minimum evidence requirements. Map these controls to NIST AI RMF and the ISO/IEC 42001 management-system framework. Assess obligations under relevant AI legislation, including the EU AI Act where applicable, against the organization's actual role and use case. [R12] [R13] [R14]

Translate policy into controls that applications and operators can enforce. A governance platform can manage records and approvals, but the runtime still needs authorization, placement checks and evidence capture. For an isolated site, select locally deployable components whose licensing and dependencies support the approved isolation profile.

Maintain the authoritative policy, use-case inventory and incident authority required by the sovereignty profile inside its approved boundary. An enterprise-wide catalog may receive permitted summaries, while the AWS European Sovereign Cloud and HPE sovereign teams retain the records and authority needed for local operation. Apply disclosure rules to governance metadata as well as AI content.

Table 2 Governance controls and evidence

| **Governance layer** | **Control enforced in the deployment domain** | **Evidence retained** |
|---|---|---|
| Policy and risk | Approved use case, owner, risk class and permitted deployment locations | Decision record, exceptions and review date |
| Data and identity | Caller identity, dataset permissions, agent identity and key access | Authorization decisions and entitlement versions |
| Models and releases | Approved model, application configuration and signed artifacts | Provenance, evaluations and deployment manifest |
| Runtime protection | Endpoint restrictions, content controls and tool authorization | Policy decisions, blocked requests and approved actions |
| Evaluation and oversight | Quality thresholds, safety tests and human approval for selected actions | Evaluation reports and approval records |
| Audit and incidents | Protected telemetry, suspension procedures and recovery controls | Incident timeline, evidence and rollback record |

Use versioned policy packages with explicit validity and compatibility rules. Open Policy Agent supports signed bundles and verification, providing one possible mechanism for distributing approved policy artifacts. The enterprise must also define version selection, revocation, freshness and rollback behavior. [R15]

For disconnected sites, approve a bounded offline validity period. Define the local procedure for an expired policy or an urgent revocation received through the approved transfer process. A WAN outage must not remove the site's ability to enforce the policy already authorized for local operation.

# 8 Protect data throughout retrieval and generation

Permission-aware retrieval must apply the caller's current entitlements before source material enters the model context. Enforce these permissions in the retrieval or application layer, and verify access again when resolving a source citation. The proposed control must handle permission changes and prevent stale access grants from exposing restricted documents.

Do not assume a knowledge-base service automatically inherits every business permission from its source systems. Bedrock documents the permissions and service roles needed to access its knowledge bases and supporting resources. Application-level authorization must address the organization's document and user entitlements. [R17]

Treat retrieved content as untrusted input. A document can carry instructions intended to influence a model or agent. OWASP identifies indirect prompt injection through external content as a risk; retrieved text must not grant permissions, select a new processing destination or authorize a tool action. [R18]

Classify embeddings, prompts and traces as part of the data lifecycle. Minimize content copied into observability systems, separate sensitive traces from operational metrics, and apply approved encryption and retention. Exports to the governance authority should contain only the metadata and evidence permitted by the local disclosure policy.

# 9 Control agent identity and authority

Give each agent a distinct workload identity with narrowly scoped credentials. Associate that identity with an approved purpose, tool set, data scope and execution environment. Avoid sharing a broad administrator identity across autonomous processes.

Place a deterministic authorization layer between the agent and its tools. It should validate the target, action, parameters, caller, data classification and execution limits. OWASP's excessive-agency guidance addresses risks arising from excessive functionality, permissions and autonomy; the proposed tool gateway implements controls against those risks. [R19]

Require human approval for selected actions such as changing production infrastructure, exporting sensitive information, committing expenditure or modifying consequential records. Bind the approval to the exact proposed action and its parameters, with an expiration time. A model-generated statement that approval exists must not authorize execution.

Make suspension operationally effective. The response procedure should revoke or disable agent credentials, deny tool access, stop new jobs and address actions already in progress. Test platform-specific cancellation and recovery procedures. Preserve the evidence needed to investigate the incident while restoring the last approved application configuration.

# 10 Govern the complete model and application lifecycle

Maintain an inventory that links each AI application to its model, data sources, owner, risk decision and deployment domain. Include fine-tuned weights and adapters, embedding models, prompt templates, retrieval rules, guardrails, tool definitions and evaluation versions.

A model registry supplies version and lifecycle records. For example, MLflow Model Registry supports model versions, aliases, metadata and lineage. The enterprise approval process must decide which registry records authorize deployment and who can modify those decisions. [R16]

Promote a signed application release through development, evaluation, approval and deployment. The release manifest should bind all security-relevant components. Reject unsigned artifacts, unexpected digests, incompatible dependencies and unapproved destinations.

Table 3 Model and application release gates

| **Release gate** | **Approval basis** | **Accountable owner** |
|---|---|---|
| Data eligibility | Source rights, classification, permitted processing and retention | Data owner |
| Model eligibility | Provenance, license, provider terms and deployment compatibility | Model owner |
| Application readiness | Retrieval authorization, tool restrictions and passed evaluations | Application and security owners |
| Production placement | Approved domain, operating dependencies, capacity and recovery | Platform and governance owners |

Run evaluations against the actual application configuration. Assess relevant task quality, unsafe behavior, information leakage, injection attempts and tool misuse. Set measurable thresholds for the use case, with test datasets authorized for the environment where evaluation runs. Record residual risks and require a new approval when a material change invalidates earlier evidence.

# 11 Define hybrid cloud flows explicitly

Route workloads using a placement policy evaluated before processing begins. Inputs should include the use case, caller entitlement, data classification, permitted destinations, approved model and policy version. Define the result when no eligible endpoint is available: queue, deny or use another explicitly approved endpoint.

Table 4 Hybrid cloud data flows

| **Flow** | **Default blueprint behavior** | **Required control** |
|---|---|---|
| Application prompt to a model | Process within the approved domain | Placement and identity decision |
| Retrieval from source systems | Retrieve only authorized content | Entitlement enforcement and protected source access |
| Model release to another domain | Promote through a separate workflow | License review, provenance and signed manifest |
| Policy update to a connected domain | Distribute through authorized channels | Signature, version and validity checks |
| Update to an air-gapped site | Import through approved physical media | Quarantine, inspection and local verification |
| Evidence to the enterprise authority | Export approved metadata or summaries | Disclosure review, minimization and integrity checks |

For example, an enterprise assistant can process approved material in AWS while a restricted engineering assistant runs on VMware or HPE within its authorized boundary. A locally retrieved restricted passage remains subject to that boundary when included in a prompt or output. Moving model weights, adapters or evaluation records also needs a disclosure decision.

Treat transfers between commercial AWS and AWS European Sovereign Cloud as explicit boundary crossings. AWS documents the separate partition and associated resource isolation. Approve the identity, transport, destination and disclosure conditions for each transfer; create independent destination resources and release approvals. [R25]

Keep governance synchronization separate from application inference. A central inventory may show deployment state and approved evidence without receiving source documents or every conversation. Mark the freshness of exported records so operators can distinguish the last report from the site's current state.

# 12 Design the disconnected operating model

A disconnected AI environment needs a local supply chain and support process. Maintain approved copies of model artifacts, container images, dependency packages, operating-system updates and evaluation tooling. Provide local identity, DNS, trusted time, certificate validation, key services and backup recovery.

Prepare inbound release bundles in a staging environment. Inspect dependencies, verify provenance and signatures, review model licenses, run relevant tests and record the approval. At the destination, quarantine and independently verify the imported bundle before promoting it into local repositories. Signature verification establishes authenticity and integrity; acceptance testing must also address the artifact's behavior.

Use a separate outbound procedure for approved reports. Minimize exported fields, classify the bundle, inspect it for sensitive content, encrypt it for the approved recipient and record custody. The strict-air-gap blueprint uses physical transfer. A connected transfer mechanism requires its own approved isolation model. [R11]

Provide local emergency authority for suspending a model or agent, rolling back an application and responding to an incident. Record the decision and reconcile permitted evidence with enterprise governance when the approved reporting process runs.

# 13 Plan resilience and operating responsibility

Size model serving using the selected model, numerical precision, context lengths, concurrency, measured throughput and latency requirements. Include retrieval, policy checks, safety processing and evidence capture in load tests. Account for GPU memory, cache growth, model-loading time and failover capacity.

Set availability, recovery and evidence-retention objectives per use case. Maintain recoverable copies of models, manifests, policy packages, indexes and keys within approved locations. A recovery plan must preserve placement rules during failover, including when the primary site is unavailable.

Use AWS's independence exercise to inform the enterprise test plan. Measure whether the AI application can authenticate, retrieve data, serve models, enforce policy and retain evidence when specified external dependencies are unavailable. Set a test duration and recovery objectives for the enterprise use case. The provider's several-hour exercise and its longer-term autonomy design goal are different forms of evidence. [R24] [R23]

Assign explicit responsibility to the AI governance authority, data owners, model owners, application teams, platform operators, security operations and site custodians. Define who can approve an exception, revoke access, authorize an export, promote a release and activate recovery. Procurement must specify support access and operating duties for each provider.

Roll out the stack through evidence-based stages.

Table 5 Deployment stages and exit criteria

| **Stage** | **Scope** | **Exit criterion** |
|---|---|---|
| Establish boundaries | Inventory use cases and define sovereignty profiles | Owners and permitted flows approved |
| Prove the application | Implement an AWS or VMware pilot within an eligible boundary | Authorization, evaluation and recovery tests pass |
| Establish sovereign operations | Deploy AWS European Sovereign Cloud or the selected HPE environment | Partition, operator, key and support boundaries verified |
| Prove disconnected operation | Validate the selected air-gapped configuration | Required workflows function with external access blocked |
| Expand production | Add workloads, sites and governance reporting | Capacity, ownership and acceptance evidence approved |

# 14 Require production acceptance evidence

Before release, demonstrate the following controls using the actual platform configuration and representative workloads:

- [ ] A workload cannot route to an unapproved region, model, service or support endpoint.

- [ ] A user cannot retrieve restricted documents, and permission changes take effect within the approved interval.

- [ ] Retrieved instructions cannot authorize a tool action or alter the processing boundary.

- [ ] A high-impact action requires a valid approval bound to its exact parameters.

- [ ] A release with an invalid signature, unexpected artifact or expired authorization is rejected.

- [ ] Agent suspension blocks new execution and addresses in-progress actions through tested procedures.

- [ ] The disconnected deployment performs inference, retrieval, enforcement, monitoring and recovery without external services.

- [ ] The European Sovereign Cloud application meets its approved continuity targets when specified external dependencies are removed.

- [ ] Commercial AWS resources cannot be substituted silently for an approved European Sovereign Cloud endpoint or identity.

- [ ] Backup restoration preserves key access, artifact provenance, policy state and placement rules.

- [ ] Exported evidence satisfies disclosure rules and identifies its reporting time and policy version.

- [ ] Failover and capacity tests meet the approved objectives for the use case.


# References

- [R1] AWS. [AWS Security Reference Architecture for AI](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture-generative-ai/gen-ai-sra.html).

- [R2] AWS. [Cross Region inference and data residency considerations](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html).

- [R3] AWS. [Data protection in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html).

- [R4] AWS. [Use the ApplyGuardrail API independently of model invocation](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-independent-api.html).

- [R5] AWS. [Use Amazon Bedrock with VPC interface endpoints](https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html).

- [R6] AWS. [Model governance with Amazon SageMaker AI](https://docs.aws.amazon.com/sagemaker/latest/dg/governance.html).

- [R7] VMware by Broadcom. [Private AI services in VMware Private AI Foundation with NVIDIA](https://blogs.vmware.com/cloud-foundation/2025/06/19/private-ai-services-new-in-vmware-private-ai-foundation-with-nvidia-in-vcf-9-0/).

- [R8] HPE. [Sovereign by design and operational control in the AI cloud era](https://www.hpe.com/us/en/newsroom/blog-post/2026/02/sovereign-by-design-designing-for-security-compliance-and-control-in-the-ai-cloud-era.html).

- [R9] HPE. [Private cloud air gapped solutions](https://www.hpe.com/us/en/solutions/cloud/air-gapped-private-cloud.html).

- [R10] HPE. [Harbor as a local container registry in Private Cloud AI](https://developer.hpe.com/blog/setting-up-harbor-as-a-local-container-registry-in-hpe-private-cloud-ai/).

- [R11] NIST. [Air gap definition](https://csrc.nist.gov/glossary/term/air_gap).

- [R12] NIST. [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework).

- [R13] ISO. [ISO IEC 42001 Artificial intelligence management systems](https://www.iso.org/standard/42001).

- [R14] European Union. [Regulation EU 2024 1689 Artificial Intelligence Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng).

- [R15] Open Policy Agent. [Signed policy bundles and verification](https://www.openpolicyagent.org/docs/management-bundles).

- [R16] MLflow. [Model Registry](https://mlflow.org/docs/latest/ml/model-registry/).

- [R17] AWS. [Permissions to access Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-permissions.html).

- [R18] OWASP. [Prompt injection](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/main/2_0_vulns/LLM01_PromptInjection.md).

- [R19] OWASP. [Excessive agency](https://github.com/OWASP/www-project-top-10-for-large-language-model-applications/blob/main/2_0_vulns/LLM06_ExcessiveAgency.md).

- [R20] AWS. [Geographic cross Region inference permissions and considerations](https://docs.aws.amazon.com/bedrock/latest/userguide/geographic-cross-region-inference.html).

- [R21] AWS. [Amazon SageMaker Model Registry](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html).

- [R22] AWS. [Permissions for cross Region Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrail-profiles-permissions.html).

- [R23] AWS. [AWS European Sovereign Cloud design goals](https://docs.aws.amazon.com/whitepapers/latest/overview-aws-european-sovereign-cloud/design-goals.html).

- [R24] AWS. [Independent operation exercise reported on November 1 2026](https://aws.amazon.com/blogs/security/inside-a-successful-aws-european-sovereign-cloud-exercise-to-demonstrate-independent-operation/).

- [R25] AWS. [Designing a secure landing zone for the AWS European Sovereign Cloud](https://aws.amazon.com/blogs/security/designing-a-secure-landing-zone-for-the-aws-european-sovereign-cloud/).

- [R26] AWS. [AWS European Sovereign Cloud launch and AI services](https://aws.amazon.com/blogs/aws/aws-european-sovereign-cloud-is-now-generally-available/).

# AWS European Sovereign Cloud domain

* Dedicated landing zone in the **`aws-eusc` partition**: separate accounts, organization,
  IAM, endpoints and pipelines. Cross-partition role assumption is not available.
* `partition_guard` blocks a deploy if credentials resolve to the commercial partition, so
  commercial resources can never silently stand in for EUSC ones.
* Keep identity, data, keys, retrieval, inference, guardrail processing, evidence and recovery
  inside the EU boundary. Test federated identity, package mirrors and external APIs for
  independence (Blueprint §4, §13).
* Verify each model, feature, capacity and endpoint in the chosen EUSC Region before
  adding it to `approved_model_ids`.

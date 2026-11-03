# VMware private cloud domain (VCF + Private AI services)

Kubernetes manifests for VMware Kubernetes Service:

* `vllm.yaml` – model endpoint (vLLM) served from the local Harbor model store, pinned by digest, offline mode.
* `ai-gateway.yaml` – Sovereign AI gateway with OPA sidecar verifying a **signed** policy bundle.
* `networkpolicy.yaml` – default-deny ingress/egress; only gateway → model and DNS allowed.

Before approving for isolated workloads, validate the full dependency set with external
access blocked: images, model downloads, certificates, DNS, NTP, telemetry, licensing (§5).

```bash
kubectl apply -k infra/vmware-private
```

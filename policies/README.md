# Policy packages

Open Policy Agent (Rego v1) policies that mirror the Python reference engine so the same
rules can be enforced inside every deployment domain, including disconnected sites.

| Package | Blueprint section | Purpose |
|---|---|---|
| `sovereign.placement` | §3, §11 | Endpoint / jurisdiction / model / data-class placement |
| `sovereign.tools` | §9 | Deterministic agent tool authorization with bound approvals |
| `sovereign.release` | §10 | Release gates over a signed manifest |

```bash
opa test policies/ -v
opa build -b policies/ --signing-key keys/policy.pem --bundle -o dist/policy-bundle.tar.gz   # signed bundle
opa run --server --bundle --verification-key keys/policy.pub dist/policy-bundle.tar.gz
```

Signed bundles provide integrity; the enterprise still defines version selection,
revocation, freshness and rollback (see `src/sovereign_ai/policy_bundle.py`).

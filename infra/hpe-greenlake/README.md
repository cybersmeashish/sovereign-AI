# HPE GreenLake sovereign and disconnected domains (Blueprint §6, §12)

The VMware manifests in `../vmware-private` are reusable on HPE Private Cloud AI Kubernetes
clusters (set `SOVAI_DOMAIN=hpe-sovereign` or `hpe-disconnected`). The disconnected site adds:

| Local service | Purpose |
|---|---|
| Identity (IdP / LDAP) | Caller + agent identity without external federation |
| HSM / KMS | Local key custody |
| Harbor | Container + model artifact mirror ([R10]) |
| OPA + signed bundles | Policy enforcement with bounded offline validity |
| Evidence log | Hash-chained, exported only through approved physical transfer |
| NTP / DNS / PKI | Trusted time, name resolution, certificate validation |

## Physical transfer workflow

```bash
# STAGING (connected): inspect, test, sign
python scripts/airgap_bundle.py build  --src staging/release-1.4.0 --out release-1.4.0.tgz --purpose model-update --custodian alice
# DESTINATION (air-gapped): quarantine, verify, promote
python scripts/airgap_bundle.py verify --bundle /media/usb/release-1.4.0.tgz --quarantine /srv/quarantine/r140
python scripts/airgap_bundle.py promote --quarantine /srv/quarantine/r140 --repo /srv/approved
```

Signature verification proves authenticity and integrity only; run acceptance tests on the
artifact's behavior before promotion.

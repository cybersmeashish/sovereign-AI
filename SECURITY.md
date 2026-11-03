# Security policy

Please report vulnerabilities privately via GitHub Security Advisories on this repository.
Do not open public issues for security problems.

* Never commit keys, tfvars, state files or real sovereignty profiles containing sensitive data.
* The HMAC signer exists for tests and labs only; production signing must use KMS / HSM-backed keys
  held inside the approved deployment boundary.

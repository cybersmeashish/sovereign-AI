# Sovereign AI control plane: inspection map

**Domain:** AI security. **Stage:** Reference implementation. **Visibility:** public.

## Review paths

- [tests/conftest.py](tests/conftest.py)
- [tests/test_evidence_airgap.py](tests/test_evidence_airgap.py)
- [tests/test_manifest.py](tests/test_manifest.py)
- [tests/test_placement.py](tests/test_placement.py)
- [tests/test_policy_bundle.py](tests/test_policy_bundle.py)
- [tests/test_retrieval.py](tests/test_retrieval.py)
- [tests/test_tool_gateway.py](tests/test_tool_gateway.py)
- [infra/aws-commercial/main.tf](infra/aws-commercial/main.tf)

## Evidence boundary

Source files and supplied tests show what can be inspected. They do not by themselves establish successful deployment, control effectiveness, client use, compliance certification, or independent review. Runtime or cloud validation should have a separate dated evidence record.

[Connected portfolio](https://github.com/cybersmeashish) · [Research notes](https://github.com/cybersmeashish/Ashish-research)

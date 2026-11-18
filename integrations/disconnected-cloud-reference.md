# Sovereign AI — disconnected-cloud integration reference

[Integration contract](https://github.com/cybersmeashish/sovereign-disconnected-cloud-security/blob/main/docs/sovereign-ai-integration.md) connects signed model-data admission, local retrieval authorization, explicitly permitted tools and filtered evidence export.

[Implementation](https://github.com/cybersmeashish/sovereign-disconnected-cloud-security/blob/main/assurance/policy.py) · [Boundary tests](https://github.com/cybersmeashish/sovereign-disconnected-cloud-security/blob/main/tests/test_assurance_policy.py) · [Measured results](https://github.com/cybersmeashish/sovereign-disconnected-cloud-security/blob/main/docs/expanded-verification.md)

The fixture permits scoped local reads and denies cross-tenant/cross-site retrieval, shell execution and unauthorized viewer actions. A valid user from another site is also denied by the local router. Model destination and downgrade checks remain distinct from the user's resource authorization.

The reference is a deterministic router with no learned model or downloaded weights. It demonstrates authorization boundaries rather than real-model prompt-injection robustness. Real weight/tokenizer/runtime inventory, index/chunk access propagation, tool side effects, durable admission freshness and model behavior evaluation remain integration work.

[Complete contributions 08–28](https://github.com/cybersmeashish/sovereign-disconnected-cloud-security/blob/main/docs/contributions-08-28.md) · [Research findings](https://github.com/cybersmeashish/sovereign-disconnected-cloud-security/blob/main/research/2026-11-18-results.md)

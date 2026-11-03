# Contributing

1. Fork and create a feature branch.
2. `make install && make all` must pass (ruff, pytest, opa test, terraform fmt).
3. Every new control must reference the blueprint section it implements and include a test that
   demonstrates the **deny** path, not only the allow path.
4. Update `docs/acceptance-criteria.md` when a change affects §14 evidence.

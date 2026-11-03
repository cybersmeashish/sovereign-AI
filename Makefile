.PHONY: install test lint opa-test tf-fmt all

install:
	pip install -e ".[dev]"

test:
	pytest -q
	@command -v opa >/dev/null && opa test policies/ -v || echo "opa not installed - skipping policy tests"

lint:
	ruff check src tests

tf-fmt:
	terraform fmt -check -recursive infra/

all: lint test

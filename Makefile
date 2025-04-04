.PHONY: lint

lint:
	ruff check .
	ruff format .

.PHONY: format

lint:
	ruff check . --fix
	ruff format .
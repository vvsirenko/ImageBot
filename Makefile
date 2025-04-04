.PHONY: lint

lint:
	ruff check .
	ruff format .

.PHONY: format

format:
	ruff check . --fix
	ruff format .


test:
	pytest --cov=. --cov-report=term-missing --cov-config=.coveragerc

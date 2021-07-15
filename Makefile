.PHONY: test
test:
	pytest -x sqla_wrapper tests

.PHONY: lint
lint:
	flake8 --config=setup.cfg sqla_wrapper tests

.PHONY: coverage
coverage:
	pytest --cov-report html --cov sqla_wrapper sqla_wrapper tests

.PHONY: install
install:
	pip install -e .[alembic,test,dev]
	createdb dbtest || true

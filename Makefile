.PHONY: test
test:
	pytest -x sqla_wrapper tests

.PHONY: lint
lint:
	flake8 --config=setup.cfg sqla_wrapper tests

.PHONY: coverage
coverage:
	pytest --cov-config=.coveragerc --cov-report html --cov sqla_wrapper sqla_wrapper tests

.PHONY: install
install:
	pip install -e .[test,dev]
	pip install -r docs/requirements.txt
	createdb dbtest || true
	pre-commit install --hook-type pre-push

.PHONY: docs
docs:
	cd docs && ./deploy.sh

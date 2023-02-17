.PHONY: test
test:
	poetry run pytest -x -vv src/sqla_wrapper tests

.PHONY: lint
lint:
	poetry run flake8 src/sqla_wrapper tests

.PHONY: coverage
coverage:
	poetry run pytest --cov-config=pyproject.toml --cov-report html --cov sqla_wrapper src/sqla_wrapper tests

.PHONY: types
types:
	poetry run pyright src/sqla_wrapper

.PHONY: install
install:
	poetry install --with dev,test,lint
	createdb dbtest -U postgres || true
	poetry run pre-commit install

.PHONY: docs
docs:
	cd docs && mkdocs serve

.PHONY: docsdeploy
docsdeploy:
	cd docs && ./deploy.sh

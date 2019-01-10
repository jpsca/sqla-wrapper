.PHONY: all

clean: clean-build clean-pyc

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

test:
	pytest -x sqla_wrapper tests

flake:
	flake8 sqla_wrapper tests

testcov:
	pytest --cov sqla_wrapper sqla_wrapper tests

coverage:
	pytest --cov-report html --cov sqla_wrapper sqla_wrapper tests

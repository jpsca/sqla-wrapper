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

lint:
	flake8 sqlalchemy_wrapper tests --ignore=E501

test:
	py.test -x tests/

test-all:
	tox

coverage:
	py.test -x --cov-config .coveragerc --cov sqlalchemy_wrapper --cov-report html tests/
	open htmlcov/index.html

publish: clean
	python setup.py sdist bdist_wheel
	twine upload dist/*

build: clean
	python setup.py sdist bdist_wheel
	ls -l dist

wheel: clean
	pip wheel --wheel-dir=wheel .

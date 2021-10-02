.PHONY: all
all:


.PHONY: dev
dev:
	pip install . --no-cache-dir


.PHONY: build
build:
	printenv
	pip install -r requirements_dev.txt
	python setup.py sdist bdist_wheel


.PHONY: lint
lint:
	flake8 terratalk/


.PHONY: test
test: lint


.PHONY: publish
publish:
	python -m twine upload dist/*

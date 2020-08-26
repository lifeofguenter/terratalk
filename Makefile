 .PHONY: all
 all:


.PHONY: dev
dev:
	pip install . --no-cache-dir


.PHONY: build
build:
	pip install -r requirements_dev.txt
	python setup.py sdist bdist_wheel


.PHONY: publish
publish:
	python -m twine upload dist/*

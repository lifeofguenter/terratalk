.PHONY: all
all:


.PHONY: dev
dev:
	pip install . --no-cache-dir


.PHONY: build
build:
	$(info )
	$(info 🛠️ building...)
	pip install -r requirements_dev.txt
	python setup.py sdist bdist_wheel


.PHONY: lint
lint:
	$(info )
	$(info ✨ linting...)
	flake8 terratalk/


.PHONY: test
test: lint
	$(info )
	$(info 🧪 testing...)
ifeq ($(TRAVIS_PYTHON_VERSION),3.9)
	coverage run --source=terratalk -m unittest discover
	coveralls
else
	python -m unittest discover
endif

.PHONY: publish
publish:
	python -m twine upload dist/*

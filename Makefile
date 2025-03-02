SHELL := bash
TERRAFORM_VERSION := 1.5.7


# Github shim
ifdef RUNNER_OS
	TRAVIS_OS_NAME := $(shell echo -n '$(RUNNER_OS)' | tr '[:upper:]' '[:lower:]')
endif
ifdef RUNNER_ARCH
ifeq ($(RUNNER_ARCH),X64)
	TRAVIS_CPU_ARCH := amd64
else
	TRAVIS_CPU_ARCH := arm64
endif
endif
ifdef PYTHON_VERSION
	TRAVIS_PYTHON_VERSION := $(PYTHON_VERSION)
endif


.PHONY: all
all:


.PHONY: dev
dev:
	pip install . --no-cache-dir


.PHONY: build
build:
	$(info )
	$(info 🛠️ building...)
	printenv
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

ifeq ($(CI),true)
	curl -sSLfo terraform.zip https://releases.hashicorp.com/terraform/$(TERRAFORM_VERSION)/terraform_$(TERRAFORM_VERSION)_$(TRAVIS_OS_NAME)_$(TRAVIS_CPU_ARCH).zip
	unzip terraform.zip -d $(HOME)/.local/bin/
	rm terraform.zip
endif
	cd '$(CURDIR)/tests' && rm -f test.plan && terraform init && terraform plan -out test.plan

ifeq ($(TRAVIS_PYTHON_VERSION),3.11)
	coverage run --source=terratalk -m unittest discover
	coveralls
else
	coverage run --source=terratalk -m unittest discover
	coverage report --skip-covered --show-missing
endif

.PHONY: publish
publish:
	python -m twine upload dist/*

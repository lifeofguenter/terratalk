SHELL := bash
TERRAFORM_VERSION := 1.0.11


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

ifeq ($(CI),true)
	curl -sSLfo terraform.zip https://releases.hashicorp.com/terraform/$(TERRAFORM_VERSION)/terraform_$(TERRAFORM_VERSION)_$(TRAVIS_OS_NAME)_$(TRAVIS_CPU_ARCH).zip
	unzip terraform.zip -d $(HOME)/bin/
	rm terraform.zip
endif
	cd '$(CURDIR)/tests' && rm -f *.plan && terraform init && terraform plan -out test.plan

ifeq ($(TRAVIS_PYTHON_VERSION),3.9)
	coverage run --source=terratalk -m unittest discover
	coveralls
else
	coverage run --source=terratalk -m unittest discover
	coverage report --skip-covered --show-missing
endif

.PHONY: publish
publish:
	python -m twine upload dist/*

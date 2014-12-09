
SHELL := /bin/bash
ENVIRONMENT := $(shell if [ "$(target)" ]; then echo "$(target)"; else if [ -e .env ]; then head -1 .env; else echo 'dev'; fi; fi)
include conf/$(ENVIRONMENT).properties
include conf/common.properties

DJANGO_DATA_ROOT ?= .django
DJANGO_DATA_ROOT := $(abspath $(DJANGO_DATA_ROOT))
DJANGO_ARGS := --settings=instance.settings --traceback
SPIDERDOG_ARGS := --home=$(DJANGO_DATA_ROOT) --settings=instance.settings

.PHONY: clean
clean:
	@rm -f .env
	@rm -f instance/.config
	@rm -f tests/*.pyc

.PHONY: fail_if_configured
fail_if_configured:
	@if [ -e .env ]; then \
		curenv="$$(head -1 .env 2>/dev/null)"; \
		if [ "$$curenv" != "$(ENVIRONMENT)" ]; then \
			echo -n "A '$$curenv' environment has been configured but the"; \
			echo " command you just ran tried to set ENVIRONMENT to '$(ENVIRONMENT)'."; \
			echo -n "If you are sure you want to reconfigure, run 'make clean'"; \
			echo " and try again."; \
			exit 1; \
		fi; \
	fi

.PHONY: configure
configure: fail_if_configured
	@echo "$(ENVIRONMENT)" > .env
	@if [ ! -e conf/.secret ]; then \
		key="$$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)"; \
		echo "SECRET_KEY := $$key" > conf/.secret; \
	fi
	@cat conf/common.properties conf/$(ENVIRONMENT).properties conf/.secret > instance/.config
	@echo "ENVIRONMENT := $(ENVIRONMENT)" >> instance/.config
	@mkdir -p etc/buildout
	@if [ ! -e "etc/buildout/.installed.cfg" ]; then \
		echo "Bootstrapping with $$(python -c 'import sys;print(sys.executable)')"; \
		python bootstrap.py; \
	fi;
	@./bin/buildout;

.PHONY: test
test:
	@make configure target=test && ./bin/python setup.py test

.PHONY: quicktest
quicktest:
	@./bin/python setup.py test

.PHONY: dev
dev:
	@make configure target=dev

.PHONY: nuke
nuke: clean
	@rm -rf .tox
	@rm -rf .django
	@rm -rf tests/__pycache__
	@rm -rf .eggs
	@rm -rf bin
	@rm -rf etc
	@rm -f .coverage

env:
	@echo $(ENVIRONMENT)

# instance commands
.PHONY: django
django:
	@./bin/django

.PHONY: assets
assets:
	@./bin/django collectstatic --noinput

.PHONY: runserver
runserver:
	@./bin/django runserver

.PHONY: shell
shell:
	@./bin/django shell

.PHONY: serve
serve: assets
	@./bin/django-server --log-file=- --reload

.PHONY: list
list:
	@./bin/instance sites --debug




MYAPP = govready-q
CFPUSH = cf push -i 1 $(CFOPTS) $(MYAPP)
VENDOR = vendor/done
STATIC = siteapp/static/vendor/done
PIP = $(shell which pip3 || which pip)

.PHONY: run key

test:
	python3 manage.py test siteapp
	python3 -m unittest discover tests

all: clean requirements migrate run

requirements: $(VENDOR) $(STATIC)

$(VENDOR): requirements.txt
	mkdir -p vendor
	$(PIP) download --dest vendor -r $< --exists-action i
	touch $@

$(STATIC): ./deployment/fetch-vendor-resources.sh
	$<
	touch $@

key := $(shell cat /dev/urandom | head -c 50 | base64)
cf_secret :=$(shell cf env $(MYAPP) | (grep -q SECRET_KEY && echo "yes" || echo "no"))

key:
ifeq ($(cf_secret),yes)
	@echo secret key already set
else
	@echo Attempting to provision secret key with nostart push:
	$(CFPUSH) --no-start
	@echo Running: cf set-env $(MYAPP) SECRET_KEY __new_secret__
	@cf set-env $(MYAPP) SECRET_KEY $(key) 1>/dev/null
endif

run: requirements key
	$(CFPUSH)

clean:
	/bin/rm -rf $(STATIC)
	/bin/rm -rf $(VENDOR)


# The only user in the 'prod' space is 'circleci' so
# noone else will deploy to name govready-q
CFSPACE ?= undefined
# documenting a few one-time steps
provision:
ifeq ($(CFSPACE),undefined)
	@echo no space defined
else
	@echo cf target -s $(CFSPACE)
	@echo cf create-service elephantsql turtle cf-$(MYAPP)-pgsql
	@echo cf create-route development dev.pburkholder.com # Example
	# PWS seems to require email/oauth, the command below fails with 'Insufficent scope'
	@echo cf create-user circleci $(CIPASSWORD)
endif

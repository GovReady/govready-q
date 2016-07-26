test:
	python3 manage.py test siteapp
	python3 -m unittest discover tests


MYAPP = govready-q
VENDOR = vendor/done
STATIC = siteapp/static/vendor/done
PIP = $(shell which pip3 || which pip)

.PHONY: run key

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
	@echo setting new secret key
	cf push $(MYAPP) --no-start
	cf set-env $(MYAPP) SECRET_KEY $(key)
endif

run: requirements key
	cf push -i 1 $(MYAPP)

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
endif

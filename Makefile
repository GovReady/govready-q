# Makefile?!
# * because it provides lightweight idempotence (if a prequisite exists, then do nothing)
# * because it provide target based commands that are easy to remember, e.g.: make run
# * because it's u
MYAPP = govready-q

# Set up provisioning details for 'dev', 'prod'
# use --no-hostname for APEX, see
#   https://docs.cloudfoundry.org/devguide/deploy-apps/manifest.html#nohosts
CFORG   = GovReady
LOG_SERVICE =$(CFENV)-pws-papertrail
SSL_SERVICE =$(CFENV)-pws-ssl
NR_SERVICE  =$(CFENV)-pws-newrelic

ifeq ($(CFENV),prod)
  APEX    = q.govready.com
  CFOPTS  = -d $(APEX) --no-hostname
else ifeq ($(CFENV),dev)
  APEX    = qdev.govready.com
  CFOPTS  = -d $(APEX) --no-hostname
  LOGDRAIN=syslog-tls://logs4.papertrailapp.com:42856
else
  CFENV   = sandbox
  APEX    = null
  LOG_SERVICE=null
  CFOPTS  = --hostname $(MYAPP)-$(CFENV)
endif

CFPUSH = cf push -i 1 $(CFOPTS) $(MYAPP)
VENDOR = vendor/done
STATIC = siteapp/static/vendor/done
PIP = $(shell which pip3 || which pip)

.PHONY: run key dburl provision wipe test

test: static
	python3 manage.py test siteapp
	python3 -m unittest discover tests

all: clean requirements migrate run

requirements: $(STATIC) $(VENDOR)

static: $(STATIC)

requirements.txt: dev_requirements.txt cf_requirements.txt
	cat $^ > $@

PILLOW=Pillow-3.3.0-cp34-cp34m-manylinux1_x86_64.whl:
vendor/$(PILLOW)
	mkdir -p vendor/
	curl -o $@ https://pypi.python.org/packages/36/2f/addd63c3bce5b5aa33ec6d2895a41d41480bd3b03f61da76b236f61f19b6/Pillow-3.3.0-cp34-cp34m-manylinux1_x86_64.whl

$(VENDOR): requirements.txt vendor/$(PILLOW)
	$(PIP) download --dest vendor -r $< --exists-action i
	@echo Need linux for PWS:
	cd vendor && https://pypi.python.org/packages/36/2f/addd63c3bce5b5aa33ec6d2895a41d41480bd3b03f61da76b236f61f19b6/Pillow-3.3.0-cp34-cp34m-manylinux1_x86_64.whl
	cf push -i 1 --hostname govready-q-sandbox govready-q
	touch $@

$(STATIC): ./deployment/fetch-vendor-resources.sh
	$<
	touch $@

# Determine if cfapp has already been provisioned:
cf_app := $(shell cf app $(MYAPP) >/dev/null && echo yes || echo no)
cfapp:
ifeq ($(cf_app),no)
	@echo Attempting to provision app $(MYAPP) by first doing nostart push
	$(CFPUSH) --no-start
else
	@echo App, $(MYAPP), already exists
endif

key := $(shell cat /dev/urandom | head -c 50 | base64)
cf_secret :=$(shell cf env $(MYAPP) | (grep -q SECRET_KEY && echo "yes" || echo "no"))
key: cfapp
ifeq ($(cf_secret),yes)
	@echo SECRET_KEY already set
else
	@echo Running: cf set-env $(MYAPP) SECRET_KEY __new_secret__
	cf set-env $(MYAPP) SECRET_KEY $(key) 1>/dev/null
endif

# target dburl sets up a cloudfoundry env variable for
# DATABASE_URL if you're not using one provided via a
# service. This target would need to change the provisioning steps (ToDo)
cf_dburl :=$(shell cf env $(MYAPP) | (grep -q DATABASE_URL && echo "yes" || echo "no"))
dburl: cfapp
ifeq ($(cf_dburl),yes)
	@echo DATABASE_URL already set
else
	@echo Using database url: $(DATABASE_URL)
	@echo Running: cf set-env $(MYAPP) $(DATABASE_URL)
	cf set-env $(MYAPP) DATABASE_URL $(DATABASE_URL)
endif

run: requirements key
	$(CFPUSH)

clean:
	/bin/rm -f requirements.txt
	/bin/rm -rf vendor
	/bin/rm -rf siteapp/static/vendor

##################### notes on provisioning/one-time commands ###########
# The only user in the 'prod' space is 'circleci' so
# noone else will deploy to name govready-q
provision: provision-space
	cf target -s $(CFENV)
	# This create-service should be in a conditional .... (todo)
	$(CFPUSH) --no-start
ifneq ($(APEX),null)
	# associate wildcard with this app and domain:
	cf map-route $(MYAPP) $(APEX) --hostname \*
endif
ifneq ($(LOG_SERVICE),null)
	cf bind-service $(MYAPP) $(LOG_SERVICE)
	cf bind-service $(MYAPP) $(NR_SERVICE)
#	cf bind-service $(MYAPP) $(SSL_SERVICE)
endif

provision-space:
	cf target -s $(CFENV)
	cf create-service elephantsql turtle pgsql-q
ifneq ($(APEX),null)
	# In org 'GovReady' add domain 'qdev.govready.com'
	cf create-domain $(CFORG) $(APEX)
endif
ifneq ($(LOG_SERVICE),null)
	cf cups $(LOG_SERVICE) -l $(LOGDRAIN)
	cf create-service newrelic standard $(NR_SERVICE)
	cf create-service ssl basic $(SSL_SERVICE)
endif

unprovision:
	cf delete $(MYAPP)
ifneq ($(APEX),null)
	cf delete-route $(APEX) --hostname \*
endif

unprovision-space: unprovision
	cf delete-service pgsql-q
	cf delete-service $(LOG_SERVICE)
	cf delete-service $(NR_SERVICE)
	cf delete-service $(SSL_SERVICE)
	cf delete-domain $(APEX)

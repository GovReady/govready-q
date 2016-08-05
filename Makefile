# Makefile?!
# * because it provides lightweight idempotence (if a prequisite exists, then do nothing)
# * because it provide target based commands that are easy to remember, e.g.: make run
# * because it's u
MYAPP = govready-q

# Set up provisioning details for 'dev', 'prod'
# use --no-hostname for APEX, see
#   https://docs.cloudfoundry.org/devguide/deploy-apps/manifest.html#nohosts
ifeq ($(CFENV),prod)
CFSPACE = prod
CFORG   = GovReady
APEX    = q.govready.com
CFOPTS  = -d $(APEX) --no-hostname
else ifeq ($(CFENV),dev)
CFSPACE = dev
CFORG   = GovReady
APEX    = qdev.govready.com
CFOPTS  = -d $(APEX) --no-hostname
else
CFSPACE = sandbox
CFORG   = GovReady
APEX    = null
CFOPTS  = --hostname $(MYAPP)-$(CFSPACE)
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

requirements: $(VENDOR) $(STATIC)

static: $(STATIC)

$(VENDOR): requirements.txt
	mkdir -p vendor/
	$(PIP) download --dest vendor -r $< --exists-action i
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
	/bin/rm -rf vendor
	/bin/rm -rf siteapp/static/vendor

##################### notes on provisioning/one-time commands ###########
# The only user in the 'prod' space is 'circleci' so
# noone else will deploy to name govready-q
CFSPACE ?= undefined
provision:
	cf target -s $(CFSPACE)
	# This create-service should be in a conditional .... (todo)
	cf create-service elephantsql turtle pgsql-q
ifneq ($(APEX),null)
	# In org 'GovReady' add domain 'qdev.govready.com'
	cf create-domain $(CFORG) $(APEX)
endif
	$(CFPUSH) --no-start
ifneq ($(APEX),null)
	# associate wildcard with this app and domain:
	cf map-route $(MYAPP) $(APEX) --hostname \*
endif

unprovision wipe:
	cf delete $(MYAPP)
	cf delete-service pgsql-q
ifneq ($(APEX),null)
	cf delete-route $(APEX) --hostname \*
	cf delete-domain $(APEX)
endif

# This would be used just once on foundry `space` to enable
# a mapping for all applications in that space. This is
# here for documentation purposes.
# To map all apps in a space 'dev' to `appname.dev.govready.com`
mapall:
	@echo cf create-domain GovReady dev.govready.com
	@echo cf create-route dev dev.govready.com
	# ^^ also need to create wildcard DNS:
	#  *.dev.govready.com CNAME foo.cfapps.io

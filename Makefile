test:
	python3 manage.py test siteapp
	python3 -m unittest discover tests
MYAPP = govready-q
VENDOR = vendor/done
STATIC = siteapp/static/vendor/done

.PHONY: run

all: clean requirements migrate run

requirements: $(VENDOR) $(STATIC)

$(VENDOR):
	mkdir -p vendor
	pip3 download --dest vendor -r requirements.txt --exists-action i
	touch $@

$(STATIC):
	./deployment/fetch-vendor-resources.sh
	touch $@

key := $(shell cat /dev/urandom | head -c 50 | base64)
run: requirements
	cf set-env $(MYAPP) SECRET_KEY $(key)
	cf push -i 1 $(MYAPP)

clean:
	/bin/rm -rf $(STATIC)
	/bin/rm -rf $(VENDOR)

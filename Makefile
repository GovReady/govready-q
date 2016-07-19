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

run: requirements
	cf push -i 1 $(MYAPP)

clean:
	/bin/rm -rf $(STATIC)
	/bin/rm -rf $(VENDOR)

MYAPP = govready-q
VENDOR = vendor/done
STATIC = siteapp/static/vendor/done
MIGRATION = .migration_done

.PHONY: run

all: clean requirements migrate run

migrate: $(MIGRATION)

./.migration_done:
	cf push -i 1 -c './init_db.sh' $(MYAPP)
	touch $@

run: $(MIGRATION)
	cf push -i 2 $(MYAPP) -c 'null'

requirements: $(VENDOR) $(STATIC)

$(VENDOR):
	mkdir -p vendor
	pip3 download --dest vendor -r requirements.txt --exists-action i
	touch $@

$(STATIC):
	./deployment/fetch-vendor-resources.sh
	touch $@

clean:
	/bin/rm -rf $(STATIC)
	/bin/rm -rf $(VENDOR)

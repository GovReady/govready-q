MYAPP = govready-q
VENDOR = vendor/done
STATIC = siteapp/static/vendor/done

.PHONY: migrate run requirements

all: clean requirements migrate run

migrate: ./.migration_done
	echo "****************************************"
	echo "Pending MySQL; migrate also runs the app"
	echo "****************************************"

./.migration_done:	requirements
	cf push -i 1 -c './init_db.sh' $(MYAPP)
	touch $@

run: migrate
	echo "****************************************"
	echo "Pending MySQL; migrate also runs the app"
	echo "****************************************"
	#cf push $(MYAPP)

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

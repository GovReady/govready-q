# Q (by GovReady)

Q is an information gathering platform for people, tuned to the specific needs of information security and compliance professionals.

---

## Development

Q is developed in Python on top of Django.

To develop locally, run the following commands:

	pip3 install -r requirements.txt
	deployment/fetch-vendor-resources.sh
	python3 manage.py migrate
	python3 manage.py load_modules
	python3 manage.py runserver

## Test kitchen

Q can be tested within test-kitchen + vagrant with Ubuntu 14.04. As this approach is not currently in use the files have been moved [to a GitHub Gist](https://gist.github.com/pburkholder/bee382bb366346ae5a5cba7286e68e11) to keep this repository less cluttered.

## Cloud Foundry (under development)

Initially, you'll need to login to CF and create a mysql service:

```
cf login -a https://api.run.pivotal.io
cf create-service cleardb spark cf-govready-q-mysql # spark is the free tier
```

Then ensure the name above, `cf-govready-q-mysql`, matches the name in `manifest.yml` e.g.,:

```yaml
applications:
- name: govready-q
  services:
     - cf-govready-q-mysql
# ... other stuff as follows ...
```

To launch, use the `make` targets, generally

```
make clean run
```

The above step will always do the migrations as they are idempotent (not changing the database unless there are new changes), then start the app. This is not designed for running with multiple instances. As Q is a pre-release application there's no need to scale to multiple instances (https://gettingreal.37signals.com/ch04_Scale_Later.php), although the app should be stateless to support running as across multiple instances later (e.g. following 12-factor principals)

Once the `cf push` step of `make run` is complete, visit the site at https://govready-q.cfapps.io

Notes:
* To vendor all of the requirements with `pip` it seems you have to have MySQL installed locally (shrug). Try `brew install mysql` on OsX.
* Suggestions for migrations at: https://docs.cloudfoundry.org/devguide/services/migrate-db.html



## Interactive Deployment

To deploy, on a fresh machine, create a Unix user named "site" and in its home directory run:

	git clone https://github.com/GovReady/govready-q q
	cd q
	mkdir local

Then run:

	sudo deployment/setup.sh

If this is truly on a new machine, it will create a new Sqlite database. You'll also see some output instructing you to create a file named `local/environment.json` containing:

	{
	  "debug": true,
	  "host": "q.govready.com",
	  "https": true,
	  "secret-key": "something random here",
	  "static": "/root/public_html"
	}

You can copy the `secret-key` from what you see --- it was generated to be unique.

For production you might also want to make other changes to the `environment.json` file:

* Set `debug` to false.
* Set the `modules-path` key to a path to the YAML module files (the default is "modules" to use the built-in modules).
* Add the administrators for unhandled server error emails (a list of pairs of [name, address]):

	"admins": [["Name", "email@domain.com"], ...]

To update, run:

	sudo -iu site /home/site/q/deployment/update.sh
	   (as root, or...)

	~/q/deployment/update.sh
	   (...as the 'site' user, or...)

	killall -HUP uwsgi_python3
	   (...to just restart the Python process (works as root & site user))

# Credits / License

Emoji icons by http://emojione.com/developers/.

This repository is licensed under the [GNU GPL v3](LICENSE.md).

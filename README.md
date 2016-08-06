# Q (by GovReady)

Q is an information gathering platform for people, tuned to the specific needs of information security and compliance professionals.

---

## TODO
TODO:
- [ ] Move psycop install `pip install -r pgsql.txt` so local installs don't need PostgreSQL

## Development

Q is developed in Python on top of Django.

To develop locally, run the following commands:

	pip3 install -r dev_requirements.txt
	deployment/fetch-vendor-resources.sh
	python3 manage.py migrate
	python3 manage.py load_modules
	python3 manage.py runserver

### Testing

To run the integration tests you'll also need to install `chromedriver` e.g., `brew install chromedriver`

The test suite is run with: `make test`

## Test kitchen (not on this branch)

Q can be tested within test-kitchen + vagrant with Ubuntu 14.04. Assuming you've installed `kitchen` (chefdk can be useful) and Vagrant, then:

```
kitchen converge
```

will bring up your instance.  Try `curl http://localhost:8000` to see it. Then login with:

```
kitchen login
```


## Cloud Foundry (under development)

To launch, use the `make` targets, generally, for the `dev` space

```
CFENV=dev make clean provision run
```

or for a sandbox deployment not using a domain apex:

```
make clean provision run
```

The above steps will always do the migrations as they are idempotent (not changing the database unless there are new changes), then start the app. This is not designed for running with multiple instances. As Q is a pre-release application there's no need to scale to multiple instances (https://gettingreal.37signals.com/ch04_Scale_Later.php), although the app should be stateless to support running as across multiple instances later (e.g. following 12-factor principals)

Once the `cf push` step of `make run` is complete, visit the site at https://govready-q.cfapps.io

Notes:
* To vendor all of the requirements with `pip` it seems you have to have PostgreSQL installed locally (shrug). Try `brew install postgresql` on OsX.
* Suggestions for migrations at: https://docs.cloudfoundry.org/devguide/services/migrate-db.html


## Interactive Deployment

To deploy, on a fresh machine, create a Unix user named "site" and in its home directory run:

	git clone https://github.com/GovReady/govready-q q
	cd q
	mkdir local

Then run:

	sudo deployment/setup.sh

(If you get a gateway error from nginx, you may need to `sudo service supervisor restart` to start the uWSGI process.)

If this is truly on a new machine, it will create a new Sqlite database. You'll also see some output instructing you to create a file named `local/environment.json`. Make it look like this:

	{
	  "debug": true,
	  "host": "q.govready.com",
	  "organization-parent-domain": "govready.com",
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

# Adding Module Content

GovReady Q content is stored in YAML files inside the `modules` directory. 

See [Schema.md](Schema.md) for documentation on writing question and answer modules.

The recommended approach to adding new modules is by symbolic link from within `modules` to a separate directory containing your content modules.

# Credits / License

Emoji icons by http://emojione.com/developers/.

This repository is licensed under the [GNU GPL v3](LICENSE.md).

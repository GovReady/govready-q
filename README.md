# Q (by GovReady)

GovReady-Q does for cyber security compliance what tax prep software does for filing taxes.

GovReady-Q helps system integrators and small businesses programmatically generate and maintain their System Security Plan (SSP) and other compliance artifacts. GovReady-Q guides your team step-by-step through FISMA’s NIST Risk Management Framework Authorization and Accreditation (A&A) with easy-to-use "compliance apps" that interact with you and each other to generate policies, plans, and evidence to impress your auditors.

When using GovReady-Q, your team selects "apps" from a compliance store. Apps represents system components, organization processes and team roles. Our open source Expert System uses the apps to interactively teach security and ask simple questions about your software and system. As your team collaboratively answers questions, the Expert System analyzes compliance and maintains human and machine-readable versions of your SSP and compliance artifacts.

GovReady-Q works with and compliments existing cyber security GRC software with user-friendly assessments, inline security training and tutorials you can customize to take your system teams step-by-step through implementing security controls and preparing control descriptions and evidence.

GovReady-Q is open source and incorporates the emerging [OpenControl](http://open-control.org) data standard for re-usable compliance content.

[Join our mailing list](http://eepurl.com/cN7oJL) and stay informed of developments.

# Target Audience
GovReady-Q was made by developers for developers who value security, but never want to hear again better technology "can't be used because its not compliant."

Our target audience is forward thinking system integrators, security and compliance teams who need faster, modern cyber security assessments and compliance aligned with their Agile practices and DevOps culture and automation. They are tired of writing SSP's by hand and need a more scale-able, self-service approach to compliance. They want to contribute to and benefit from a supply chain of shared, re-usable, Don't Repeat Yourself compliance content.  

The compliance apps and Expert System are under heavy, active development. GovReady Q should only be used at this time by those capable and comfortable of working with pre-release software.

---

## Development

Q is developed in Python 3 on top of Django.

To develop locally, run the following commands:

	sudo apt-get install python3-pip unzip # or appropriate for your system
	pip3 install -r requirements.txt
	./fetch-vendor-resources.sh
	python3 manage.py migrate
	python3 manage.py load_modules
	python3 manage.py loaddata deployment/docker/modulesources.json
	python3 manage.py createsuperuser
	python3 manage.py runserver

The module dependency diagrams also require that you have `graphviz` installed (e.g. `apt-get install graphviz`).

If you don't want to get logged out on each restart of the runserver process, copy what it shows you into a new file at `local/environment.json` like this:

    {
      "debug": true,
      "host": "localhost:8000",
      "https": false,
      "secret-key": "...something here..."
    }
    
(It will give you a fresh `secret-key` on each run that you can actually use.)

You must set up the first organization (i.e. end-user/client) domain from the Django admin. Log into http://localhost:8000/admin with the superuser account that you created above. Add a Siteapp -> Organization (http://localhost:8000/admin/siteapp/organization/add/). Then visit the site at subdomains.localhost:8000 (using the subdomain for the organization you just created) and log in using the super user credentials again. (If you are using a domain other than `localhost`, then you must set it as the value of `"organization-parent-domain"` in the `local/environment/json` file.) When you log in for the first time it will ask you questions about the user and about the organization.

We have some Q modules (i.e. question-answer definitions) stored in a separate repostiory. At this point you may need to get those modules, create a symlink from `modules/something` (here) to the modules directory in the other repository. Then run `python3 manage.py load_modules` again.

Once the modules are loaded, you can create the first "project" a.k.a. "system" and then start answering questions.

After logging in as the superuser, you will probably want to invite non-superusers into the organization from within the application (from organization settings or project settings) and then possibly switch to that account. The debug server is configured to dump all outbound emails to the console. So if you "invite" others to join you within the application, you'll need to go to the console to get the invitation acceptance link.

## Testing

To run the integration tests you'll also need to install `chromedriver` e.g., `brew install chromedriver`

The test suite is run with: `./manage.py test`

We have continuous integration set up with CircleCI at https://circleci.com/gh/GovReady/govready-q.

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
	  "organization-seen-anonymously": false,
	  "https": true,
	  "secret-key": "something random here",
	  "static": "/root/public_html"
	}

You can copy the `secret-key` from what you see --- it was generated to be unique.

For production you might also want to make other changes to the `environment.json` file:

* Set `debug` to false.
* Set `module-repos` to access module definitions not in this repository, see below.
* Add the administrators for unhandled server error emails (a list of pairs of [name, address]):

	"admins": [["Name", "email@domain.com"], ...]

To update, run:

	sudo -iu site /home/site/q/deployment/update.sh
	   (as root, or...)

	~/q/deployment/update.sh
	   (...as the 'site' user, or...)

	killall -HUP uwsgi_python3
	   (...to just restart the Python process (works as root & site user))

# Apps and Module Content

Content in Q is organized around apps and modules:

* A "module" is a linear sequence of questions that produces zero or more output documents.
* An "app" is a collection of modules, one of which is named "app" that defines the layout of the app when it is started by a user.

Modules are stored in YAML files. Built-in apps and modules are stored inside the `modules` directory in this repository. Other apps and modules are stored in other repositories that can be linked to a Q deployment through the `ModuleSource` model in the Django admin.

See [Apps.md](Apps.md) for documentation on creating apps and having them appear in the Q app catalog.

See [Schema.md](Schema.md) for documentation on writing modules, which contain questions.

# Testing and Generating Screenshots

It is possible to create a PDF containing screenshots of a module being completed automatically:

* You must have the module loaded into your local database using `load_modules`.

* Then create a fixture using the `create_fixture` management command containing a test user & test organization plus the modules you need to run the test.

* Finally use the `take_module_screenshots` management command to start a Selenium browser session and take screenshots. Give it the fixture file and the ID of a question in the project specified in the `create_fixture` command.

Like this:

	./manage.py load_modules
	./manage.py create_fixture local/ssp/project > /tmp/ssp.json
	./manage.py take_module_screenshots /tmp/ssp.json fisma_level


# Credits / License

Emoji icons by http://emojione.com/developers/.

This repository is licensed under the [GNU GPL v3](LICENSE.md).

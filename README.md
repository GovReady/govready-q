# GovReady-Q Compliance Server

GovReady-Q Compliance Server is an open source tool to help teams build and operate compliant IT systems.

1. [About GovReady-Q Compliance Server](#about-govready-q) 
1. [Installation / Deployment](#installation)
	1. [Installing](#installing)
	1. [Create an Organization](#create-org)
	1. [Updating](#updating)
1. [Development](#development)
1. [Understanding Compliance Apps](Apps.md)
1. [Automation API](Automation.md)

# <a name="about-govready-q"></a>About GovReady-Q Compliance Server
GovReady-Q offers easy-to-use "compliance apps" that manage and generate documentation of your IT systems. Compliance apps represents system components, organization processes and team roles. When using GovReady-Q, your IT project teams select "apps" from a compliance store. The apps interactively teach security and ask simple questions about your software and system. As you pick apps and collaboratively answers questions with your team, GovReady-Q analyzes tracks your system's compliance and maintains human and machine-readable versions of your compliance documentation.

GovReady-Q can be used on its own or as a compliment to an organization's existing GRC software providing step-by-step guideance and pre-written control implementation descriptions.

GovReady-Q is in public beta and recommended for innovators and early adopters interested in furthering the platform's development.

Our vision is to make Governance, Risk and Compliance easy and pratical for small businesses, developers, managers, and others who are not security or compliance experts.

GovReady-Q is open source and incorporates the emerging [OpenControl](http://open-control.org) data standard for re-usable compliance content.

[Join our mailing list](http://eepurl.com/cN7oJL) and stay informed of developments.

# <a name="installation"></a>Installation / Deployment

## <a name="requirements"></a>Requirements

GovReady-Q Compliance Server requires the following:

* Python3
* Django
* SQL Database (SQLITE3, Postgres, MariaDB, MySQL)
* PIP for Python3
* Various Python3 libraries
* Web server (Apache or NGINX for production)

## <a name="installing"></a>Installing

Guides for installing and deploying GovReady-Q on different Operating Systems can be found the `deployment` directory.

* [Launching with Docker](deployment/docker/README.md) - super easy and has a nice `first_run.sh` script
* [Installing on RHEL](deployment/rhel/README.md) - detailed instructions on installing, libraries, setting up Postgres and Apache
* [Installing on Ubuntu](deployment/ubuntu/README.md) - super easy `update.sh`

Once you have the libaries installed, you will need to clone the repository and run the Django commands to set up the database tables. GovReady-Q will create an SQLite3 database by default and can be configured to work with Postgres, MariaDB, or MySQL.

	# clone repo
	git clone https://github.com/GovReady/govready-q q
	cd q
	
	# create local director
	mkdir local

	# install python packages
	pip3 install -r dev_requirements.txt
	
	# install other assets
	./fetch-vendor-resources.sh
	
	# create database tables
	python3 manage.py migrate
	
	# misc
	python3 manage.py collectstatic --noinput

	# set up admin user
	python3 manage.py first_run

 
 When complete, a `local/environment.json` will have been generated. Make it look like this:

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

Follow the guides for instructions on launching GovReady-Q.

If you are developing locally, GovReady-Q can be run with Django's built-in web server with this command:

	python3 manage.py runserver


## <a name="create-org"></a>Create an Organization

You must set up the first organization (i.e. end-user/client) domain from the Django admin. Log into http://localhost:8000/admin with the superuser account that you created above. Add a Siteapp -> Organization (http://localhost:8000/admin/siteapp/organization/add/). Then visit the site at subdomains.localhost:8000 (using the subdomain for the organization you just created) and log in using the super user credentials again. (If you are using a domain other than `localhost`, then you must set it as the value of `"organization-parent-domain"` in the `local/environment/json` file.) When you log in for the first time it will ask you questions about the user and about the organization.


GovReady-Q currently installs with a small set of compliance apps primarily for demonstration purposes. Compliance apps are data definitions written in YAML. Organizations can and should plan to develop their own compliance apps, just as they would develop their own configuration files. The principle benefit of compliance apps is their modularization and reusability.


## <a name="updating"></a>Updating

If you have installed GovReady-Q from a clone of this repository, you can update your copy by running the `deployment/update.sh` script. The `update.sh` script will use git to pull the latest version of GovReady-Q, run migrations, and install new any new Python modules.

To update, run:

	sudo -iu site /home/site/q/deployment/update.sh
	   (as root, or...)

	~/q/deployment/update.sh
	   (...as the 'site' user, or...)

	killall -HUP uwsgi_python3
	   (...to just restart the Python process (works as root & site user))


# <a name="development"></a>Development

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

# Apps and Module Content

Content in Q is organized around apps and modules:

* A "module" is a linear sequence of questions that produces zero or more output documents.
* An "app" is a collection of modules, one of which is named "app" that defines the layout of the app when it is started by a user.

Modules are stored in YAML files. Built-in apps and modules are stored inside the `modules` directory in this repository. Other apps and modules are stored in other repositories that can be linked to a Q deployment through the `ModuleSource` model in the Django admin.

See [Apps.md](Apps.md) for documentation on creating apps and having them appear in the Q app catalog.

See [Schema.md](Schema.md) for documentation on writing modules, which contain questions.

# Testing and Generating Screenshots

## Testing

To run the integration tests you'll also need to install `chromedriver` e.g., `brew install chromedriver`

The test suite is run with: `./manage.py test`

We have continuous integration set up with CircleCI at https://circleci.com/gh/GovReady/govready-q.

## Generating screenshots

It is possible to create a PDF containing screenshots of a module being completed automatically:

* You must have the module loaded into your local database using `load_modules`.

* Then create a fixture using the `create_fixture` management command containing a test user & test organization plus the modules you need to run the test.

* Finally use the `take_module_screenshots` management command to start a Selenium browser session and take screenshots. Give it the fixture file and the ID of a question in the project specified in the `create_fixture` command.

Like this:

	./manage.py load_modules
	./manage.py create_fixture local/ssp/project > /tmp/ssp.json
	./manage.py take_module_screenshots /tmp/ssp.json fisma_level


# <a name="license"></a>License / Credits

This repository is licensed under the [GNU GPL v3](LICENSE.md).

Emoji icons by http://emojione.com/developers/.


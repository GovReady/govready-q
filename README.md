# Q (by GovReady)

Q is an information gathering platform for people, tuned to the specific needs of information security and compliance professionals.

---

## Development

Q is developed in Python 3 on top of Django.

To develop locally, run the following commands:

	sudo apt-get install python3-pip unzip # or appropriate for your system
	pip3 install -r requirements.txt
	./fetch-vendor-resources.sh
	python3 manage.py migrate
	python3 manage.py load_modules
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

# Adding and Accessing Module Content

GovReady Q content is stored in YAML files. Built-in modules are stored inside the `modules` directory in this repository. Other modules are stored in other repositories. 

See [Schema.md](Schema.md) for documentation on writing question and answer modules.

Your Q deployment can pull module content from local directories and Github by listing the module sources ("repositories") in the `module-repos` key in the `environment.json` file. For example:

	...
	"module-repos": {
		"system": {
			"type": "local",
			"path": "modules/system"
		},
		"my_modules/one": {
			"type": "git",
			"url": "git@github.com:GovReady/my-modules",
			"branch": "master",
			"path": "modules",
			"ssh_key": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
		},
		"my_modules/two": {
			"type": "github",
			"repo": "GovReady/my-modules",
			"path": "modules",
			"auth": { "user": "...", "pw": "..." }
		},
	}
	...

Each entry in `module-repos` binds a namespace in your local deployment (in this example: `system`, `my_modules/one`, and `my_modules/two`) to a repository of modules. All deployments must have the `system` namespace bound to the modules at the local path `modules/system`. The repositories can be of these types:

* `"type": "local"` to load modules from a directory on the local file system. Specify a relative or absolute path in `path`.

There are two ways to pull modules from Github:

* `"type": "git"`, where you specify the `https:...` or `git@...` URL of a git repository in the `url` field and, optionally, a branch name. If the repository requires authentication, you can put an SSH private key such as a [Github deploy key](https://developer.github.com/guides/managing-deploy-keys/) in the `ssh_key` field (paste the whole key using `\n` for newlines, not a filename).

* `"type": "github"`, which uses the Github API and user credentials such as a Github username and a [personal access token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/). Since the `github` method requires user credentials, it should be avoided for production deployments in favor of the `git` method with a deploy key if necessary.

Both git methods have an optional `path` field which lets you choose a directory _within_ the git repository to scan for module YAML files.

After making changes to `module-repos`, run `python3 manage.py load_modules` to pull the modules from the module repositories into the database.

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

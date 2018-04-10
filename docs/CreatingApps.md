# Creating GovReady-Q Compliance Apps using the Docker version

This is a step-by-step guide to creating compliance apps using the Docker version of the GovReady-Q Commpliance Server.

In this guide you will learn how to:

* Start and configure the Docker version of GovReady-Q
* Create a compliance app
* Edit a compliance app's YAML files
* Edit a compliance app using GovReady-Q's authoring tools
* Deploy the app to a production instance of GovReady-Q and storing apps in a source code version control repository

## Step 1: Prepare your local environment

### Create a folder on your workstation

GovReady-Q compliance apps are generally developed in an off-line development environment, usually on the app developer's macOS or Linux workstation --- any environment that can run Docker. In this environment, the compliance app data files will be stored in a local directory. This guide assumes the use of a local workstation for development and discusses production deployment at the end.

(Once the apps are ready to be published to the rest of the organization, the apps can be uploaded to a git repository, such as Github or an on-premis equivalent. The production instance of GovReady-Q will typically read compliance apps from the git repository directly and not from a local disk.)

On the development workstation, create a folder to hold GovReady's install script, the GovReady-Q database (in development, Sqlite is used), and the compliance apps that you will be authoring. The folder can be anywhere:

	mkdir /path/to/dev_directory
	cd /path/to/dev_directory

### Install Docker

If you haven't already done so [install Docker](https://docs.docker.com/engine/installation/) on the workstation and, if appropriate, [grant non-root users access to run Docker containers](https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (or else use `sudo` when invoking Docker below).


## Step 2: Install the GovReady-Q Compliance Server, Docker version

### Starting the Docker container

Next download GovReady's [docker\_container\_run.sh](docker_container_run.sh) script. This script simplifies passing various settings to create and configure the `govready-q` docker container that we will use for local development.

	wget https://raw.githubusercontent.com/GovReady/govready-q/master/deployment/docker/docker_container_run.sh
	chmod +x docker_container_run.sh

`docker_container_run.sh` supports a variety of [advanced configuration settings](README.md#advanced-configuration) via command line parameters. The ones we care about for developing compliance apps are:

* `--sqlitedb /path/to/govready-q-database.sqlite`, which sets an absolute path to a Sqlite database that holds all persistent information across container runs
* `--appsdevdir /path/to/apps`, which sets an absolute path to the directoy in which app YAML files will be developed
* `--relaunch`, which removes any existing `govready-q` Docker container if one is running

Download and start GovReady-Q:

	./docker_container_run.sh --sqlitedb `pwd`/database.sqlite --appsdevdir `pwd`/apps --relaunch

Note that `pwd` is used to ensure the paths are absolute.

The script will download the [govready/govready-q image](https://hub.docker.com/r/govready/govready-q/) from the Docker Hub, which could take a few minutes. It will then start a new Docker container named `govready-q` and will launch the Q source code within it.

When the container is launched it will let you know the URL to visit:

	GovReady-Q has been started!
	Container Name: govready-q
	Container ID: d99e8ac2d6a761cfd7be7f94bd01d5f7115efd66714064f7b1f0f6c09b74c269
	URL: http://localhost:8000

(You can change the hostname and port by adding e.g. `--address q.company.com:8010`.)

It takes about 15 seconds for the GovReady-Q server to be ready. Open the URL (e.g. http://localhost:8000) and reload a few times until the GovReady-Q Compliance Server becomes available:

![First run of GovReady-Q](assets/firststart.png)

### Setting up your organization and administrative user

Now that the GovReady-Q Compliance Server is running, create an administrative account and an organization. Run the following command and answer the prompts:

	docker container exec -it govready-q first_run

Your prompt and reply will look something like this:

	Installed 2 object(s) from 1 fixture(s)
	Let's create your first Q user. This user will have superuser privileges in the Q administrative interface.
	Username: admin
	Email address: admin@mycompany.com
	Password: 
	Password (again): 
	Superuser created successfully.
	Let's create your Q organization.
	Organization Name: The Company, Inc.   

Now return to your browser, reload the page, and notice the company name has updated:

![First run of GovReady-Q with the organization configured](assets/firststart2.png)

You can now sign in with the administrative username and password you created.

![First run after logging in](assets/firststart3.png)

Congratulations! You've installed GovReady-Q Compliance Server configured for local development of compliance apps!


## Step 3: Creating a compliance app

### Creating the app

In this section we'll create our first compliance app. The app will appear in the compliance apps catalog in GovReady-Q. Click `Add other app` in your browser to go to the compliance apps catalog.

![Compliance apps catalog](assets/appcatalog.png)

Let's create our first commpliance app! Use the command below:

	docker container exec -it govready-q ./manage.py compliance_app host myfirstapp

The output will be:

	Created new app in AppSource host at /mnt/apps/myfirstapp

The path shown in the output is a path _within_ the container's filesystem, which is inaccessible from the workstation. The actual path is inside the path given to the `--appsdevdir` command line argument previously. If you followed our steps above exactly, you can see the app's files in your `apps` folder:

	$ ls -l apps/myfirstapp
	-rw-r--r-- 1 root root  664 Oct 25 11:43 app.yaml
	drwxr-xr-x 2 root root 4096 Oct 25 11:43 assets
	-rw-r--r-- 1 root root  449 Oct 25 11:43 example.yaml

Head back to your browser and reload the compliance apps catalog page.

Your new app may not appear because the catalog is cached. To clear the cache, restart the container:

	docker container restart govready-q

After a few moments the container will be back up. Reload the compliance app catalog page. You should now see your app if you scroll to the end:

![Compliance apps catalog with your first app](assets/appcatalog2.png)

The development directory on the workstation now holds:

	.
	├── apps
	│   └── myfirstapp
	│       ├── app.yaml
	│       ├── assets
	│       │   └── app.png
	│       └── example.yaml
	├── database.sqlite
	└── docker_container_run.sh

(More information about the structure of the app directory can be found in [Apps.md](../../Apps.md).)

### Editing app catalog metadata

Open `apps/myfirstapp/app.yaml` in a text editor. Edit the short description and add some text describing the app you are building:

	  description:
	    short: |
	      Achieve compliance for our organization's systems.

Since this file was created by Docker, which is running as root, the file will be owned by root. You may need to use sudo to edit this file.

Reload the container to clear the app catalog cache:

	docker container restart govready-q

And then reload the catalog page in your browser to see your description beneath `myfirstapp`. You can also edit the app's title and other catalog metadata, including the app's icon in `apps/myfirstapp/assets/app.png`.

![Compliance apps catalog after metadata change](assets/appcatalogafterchange.png)

## Step 4: Edit the compliance app's YAML files

### Start the app

In your browser, click on the `myfirstapp` entry's Add button in the app catalog.

![The new app](assets/startedapp.png)

### About editing the app

We can edit our new compliance app by editing its `app.yaml` and `example.yaml` files on disk in our favorite text editor (described in this section) or with GovReady-Q's built-in authoring tools (described in the next section).

After each edit to the compliance apps files on disk, it may be necessary to restart the Docker container if you modified app catalog metadata (as you did above with `docker container restart`) or start a new instance of the compliance app from the compliance apps catalog page in your browser, if you modified the app's questions and output templates.

GovReady-Q purposely does not automatically recognize changes to compliance apps on disk until a new instance of the app is selected or a reload command (described below) is issued. This ensures previously loaded versions of the compliance app correctly maintain data entered by end-users.

### Editing the app's main page

The opening screen of the app is determined by the `questions` section of the `app.yaml` file:

	questions:
	- id: q1
	  title: Example Module
	  type: module
	  module-id: example

The new app has a single question labeled by the title `Example Module`, as you see in the YAML and in your browser. When the user clicks Example Module in the browser, they will start a new module defined by the YAML file referenced in the `module-id` data, in this case `example.yaml`.

Edit the `title` to:

	  title: Start Compliance

As described above, reloading the page in the browser will not show the change. This is by design. Since you are developing an app on your local filesystem, the GovReady-Q authoring tools are available.

Click `Authoring Tool` in the right column, and then click `Reload App from local filesystem`. (Alternatively, you could return to the compliance app catalog page and add the app again.)

![Module authoring tools](assets/authoringtools.png)

Note how `Start Compliance` now appears in the browser.

![Reloaded app](assets/reloadedapp.png)

### Editing the app's first module

Click `Start Compliance`. This begins the app's module defined in `example.yaml`. The example module contains a single sample question:

![The new app's sample question](assets/samplequestion.png)

Open `example.yaml` and see that the question's type, prompt, and choices are defined in the YAML file's `question`'s section:

	questions:
	- id: q1
	  title: What is your favorite science fiction franchise?
	  prompt: What is your favorite science fiction franchise?
	  type: choice
	  choices:
	    - key: startrek
	      text: Star Trek
	    - key: starwars
	      text: Star Wars
	    - key: lordoftherings
	      text: Lord of the Rings
	    - key: other
	      text: Other

Change the `prompt` or `choices`.

(As with `app.yaml`, since this file was created by Docker the file will be owned by root. You may need to use sudo to edit this file.)

As described above, reloading the page in the browser will not show the change. This is by design. Go back to the main app page, click `Authoring Tool` and then `Reload App from local filesystem`, and then go back to the Start Compliance page.

Your changes are now seen in your browser.

![The revised question](assets/revisedquestion.png)

More information about the file format of modules can be found in [Schema.md](../../Schema.md).

## Step 5: Edit a compliance app using GovReady-Q's authoring tools

### About the authoring tools

It is also possible to edit a compliance app's questions without leaving your browser. When editing the compliance app via GovReady-Q's built-in authoring tools, you will immediately see the changes in the instance of the compliance app you are editing without having to reload it. The changes are also immediately written to the files on disk.

GovReady-Q's built-in authoring tools will let you edit and add questions, but currently won't let you change the name of the description of the app in catalog. You will still need to edit those details in the compliance app YAML files stored on disk, as described above.

### Editing a question

A blue pencil icon will appear at the top right of module questions when the authoring tools are available. Click the pencil icon for the sample question. The question editor will pop up:

![Question authoring tool](assets/authoringtoolquestion.png)

This is a much easier way of editing questions! Try editing this question. After clicking `Save Changes`, look in your text editor to see that the changes have been immediately saved to `example.yaml`.

### Adding questions

It is also possible to add questions. In order to add a question, all of the existing questions must be answered. Answer the sample question, or click `Skip`.

You'll see an `Add Question` button on the module review page:

![Add question button](assets/addquestion.png)

Try out the Add Question button now. It will create a new text question. Use the blue pencil icon to change the question's prompt and choices.

You have now seen how to create and edit an app!

## Step 6: Deploy the app to a production instance of GovReady-Q

### Adding apps to a git repository

Your workstation's instance of GovReady-Q has been configured to load apps from the local filesystem. Your organization's production instance of GovReady-Q can be configured similarly, but more likely it will be configured to load apps from a remote git repository.

Create a new git repository in your source code control system and push your `apps` directory to the repository. The repository's root directory should contain a directory named `myfirstapp`:

	repository root
	  └── myfirstapp
	      ├── app.yaml
	      ├── assets
	      │   └── app.png
	      └── example.yaml

If you have an existing source code control system containing apps in this layout, consider checking out the repository locally so that it is in the same path provided to the `--appsdevdir` argument to `docker_container_run.sh`. If your repository is in a different layout or if you are using multiple repositories to store compliance apps, see below.

### Configuring a production system to load apps from the git repository

On the production GovReady-Q instance, log into the Django admin at `https://production-q/admin`. Add a new `AppSource`.

Set its `Namespace` to anything short composed of letters, numbers, and underscores. It might be based on the name of the repository holding the apps.

Set its `Spec` to a JSON data structure describing where to load the apps from. In this example the apps are in a private repository on Github:

	{
	    "type": "git",
	    "url": "git@github.com:your-org/your-apps",
	    "branch": "master",
	    "ssh_key": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
	}

With this method you can give access to a private Github repository. Set the `ssh_key` to a JSON-encoded string (i.e. replace newlines with `\n`) holding an SSH private key corresponding to a public key that has been added to the repository as a deploy key. Using the `jq` tool available in most package managers, it's easy to get the JSON-encoded string for a private key by running:

	cat ~/.ssh/id_rsa | jq -Rs

As with local development, the production system's compliance app catalog may be cached. To see new apps, restart the production instance of GovReady-Q.

See [Apps.md](../../Apps.md) for more information about how to configure your production instance of GovReady-Q to load apps from local filesystem directories, git repositories (including on-prem git repositories), or Github.

### Advanced setups for development with a repository of apps

In this guide we have used the `--appsdevdir` command to specify a location in which app YAML files and assets are stored. In a small setup, all apps could be stored in a subdirectory of the location given to `--appsdevdir`. But you may want to separate apps into different folders, such as if they are divided between folders in a single git repository or across multiple git repositories, then a more advanced configuration of GovReady-Q is necessary.

Imagine the following directory structure where two Github repositories are cloned into two separate local directories within `apps`, and each has a `compliance_apps` directory holding its apps:

	.
	├── apps (`--appsdevdir` directory)
	│   ├── repo1
	│   │   └── compliance_apps
	│   │       ├── myfirstapp
	│   │       └── mysecondapp
	│   └── repo2
	│       └── compliance_apps
	│           ├── mythirdapp
	│           └── myfourthapp
	├── database.sqlite
	└── docker_container_run.sh

The default setup from GovReady-Q docker installation only show apps in the compliance app catalog if the app files are located in the immediate subdirectory of path configured to load apps. But we can also tell GovReady-Q to load apps from *multiple* locations. In this case we will configure GovReady-Q to load apps from two locations:

	apps/repo1/compliance_apps
	apps/repo2/compliance_apps

Recall that the path given to `--appsdevdir` is mapped to a path within the Docker container so that the container can see the YAML files on the (host) local filesystem. The container sees these directories as

	/mnt/apps/repo1/compliance_apps
	/mnt/apps/repo2/compliance_apps

Log into the Django admin at `http://localhost:8000/admin`. Add two new `AppSource` entries:

For the first, set the `Namespace` to `repo1` (or any other label that will help you distinguish the two repositories) and the `Spec` to

	{
	  "type":"local"
	  "path":"/mnt/apps/repo1/compliance_apps",
	}

For the second, set the `Namespace` to `repo2` and the `Spec` to

	{
	  "type":"local"
	  "path":"/mnt/apps/repo2/compliance_apps",
	}

Then restart the container:

	docker container restart govready-q

and the apps defined in all of the repositories should be visible in the compliance app catalog.

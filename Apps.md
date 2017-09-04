# More About Compliance Apps

As described in the primary [README](README.md), Compliance apps map IT System components to compliance controls. A "component" can be any part of a system that contributes to its operation including organizational processes.

Compliance apps collect and assess information about one or more system components and translate that information to compliance documentation.

![Apps map components to security/compliance controls](docs/assets/app_diagram2.png)

Compliance apps can collect information about a system component from people (via web-based questionnaires) and from system components (via an [Automation API](Automation.md)).

# Compliance Apps are Collections of Modules

A Compliance app is a collection of "modules" for gathering information. A module is a collection of questions and output documents. A module can have just questions and output documents, just output documents and no questions, or both questions and output documents.

An "app" is a collection of "modules," one of which must be named "app." Modules are linear sequence of questions presented to users that produces zero or more output documents. Modules are stored in YAML files. Output documents of various types are supported such as markdown, HTML, and YAML. (See [Schema.md](Schema.md) for documentation on writing modules.)

The typical user experience will be to first pick a "top level" app from the compliance catalog representative of IT System, then pick the "component" apps that represent the specific components of the IT System, and then iteratively complete the questions within the component apps modules.

Technically speaking, a top level app is a module containing questions whose answers are other apps.

The below diagram depicts an exploded view of the relationships between a top level app to a component app to modules and questions.

!["Top Level" compliance apps contain "component" compliance apps that contain modules and questions](docs/assets/app_exploded.png)


## App Structure

Each app is defined by a set of YAML files and asset files stored in the following directory structure:

    app_name
	├── app.yaml
	├── assets
	│   ├── app.png
	│   ├── image_one.yaml
	│   ├── image_two.yaml
	│   └── ...
	├── module_one.yaml
	├── module_two.yaml
	└── ...

By convention, each app is required to have `app.yaml` file which includes metadata for the displaying the app in the catalog and an `assets/app.png` graphic which displays as the app's icon.

`app.yaml` is a required file in every app which includes app catalog metadata, such as the app's description, as well as module questions which define the layout of the app's main screen once it is started by the user.

Other module YAML file may be includes in the app as well, as needed.

The `assets` subdirectory can contain any static assets that will be served when showing the app's modules for the user, such as images included in document templates. A file typically named `app.png` in the assets directory is the app's icon, which is displayed when browsing the app catalog as well as when the app is used within another app, if `icon: app.png` is specified in `app.yaml`.


## App YAML

The `app.yaml` file that exists in every app serves two purposes:

1. It includes app catalog information, i.e. metadata, that will be shown in the app directory, such as the app's short and long description, version number, vendor, etc.
1. It also defines a module (see [Schema.md](Schema.md)) which defines the top-level layout of the app. The module may only contain questions whose type are `module` or `module-set`.

The `app.yaml` file looks like this:

![App structure](docs/assets/app_structure_sm.png)


	id: app
	title: My App
	type: project
	icon: app.png # refers to file in app's assets directory
	protocol: globally_unique_protocol_name # for inner apps only

	catalog:
	  categories:
	    - Category Name
	    - Another category name
	  vendor: GovReady PBC
	  vendor_url: https://www.govready.com
	  status: Operational
	  version: 0.6
	  source_url: https://github.com/GovReady/govready-app-example
	  description:
	    short: |
	      One-line description of the app here, using Markdown.
	    long: |
	      Long description of the app here.

	      It can be multiple paragraphs and is Markdown.
	  recommended_for:
	    - key_short: Org
	      value: Medium
	    - key_short: Tech
	      value: Drupal
	    - key_short: Role
	      value: Dev

	questions:
	  - id: item1
	    title: Do A Thing
	    type: module
	    module-id: module1 # refers to module1.yaml within this app
	    tab: TabName
	    group: GroupName
	  ... more questions here ...

	output:
	  - tab: TabName
	    format: markdown
	    template: |
	      This (optional) content will appear at the top of the TabName tab.

The questions in the app YAML file can only be of type `module` and `module-set`. The questions can specify a `module-id` to refer to another module within the same app or a `protocol` to allow the user to choose any app that has a matching `protocol` value set at the top level of the YAML file.

A `module` YAML structure is identical to `app.yaml` structure but without the catalog details section.

## Top Level Apps

Apps that describe the required components of a compliant IT system are considered "Top Level" apps. Each question in a Top Level app specifies a type of compliance app (e.g., a compliance app "protocol") that is needed to represent that component.

## App Sources

Apps are loaded into Q from an "app source," which can be a local directory, a Github repository, etc. App sources are linked to a Q deployment through the `ModuleSource` model in the Django admin.

A Q deployment can pull module content from various sources --- including local directories and git repositories --- by creating Module Sources in the Django admin site at [/admin/guidedmodules/modulesource/](http://localhost:8000/admin/guidedmodules/modulesource/). Each Module Source specifies a virtual filesystem from which apps are located.

### App Source virtual filesystem layout

Whether the source is a local directory or a git repository, the source must have a directory layout in which each app is stored in its own directory. (The directory name becomes an internal name for the app.) For instance:

	app1/app.yaml
	app1/...other_app1_files
	app2/app.yaml
	app2/...other_app2_files
	...

### App Source JSON "Spec" field

Each Module Source has a `Spec` field which contains a JSON definition of how to fetch module YAML files. The default Module Source for system modules uses the following Spec string:

	{
	  "type":"local"
	  "path":"modules/system",
	}

This Spec string says to find module YAML files on the local file system at the path `modules/system`, which is relative to the root of this git repository. (An absolute local path could be used instead.)

In addition to the Spec string, each Module Source has a namespace. Each source binds a namespace in your local deployment to a source of modules.

All deployments must have a Module Source that binds the `system` namespace to the modules at the local path `modules/system`, as in the Spec string above. This Module Source is created during the first run of `manage.py migrate` for you.

The `Spec` field of Module Sources can be of these types (explanation follows below):

	Local file system source:
	{
		"type": "local",
		"path": "modules/system"
	}

	Git repository source using a URL:
	{
		"type": "git",
		"url": "git@github.com:GovReady/my-modules",
		"branch": "master",
		"path": "modules",
		"ssh_key": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
	}

	Github repository using the Github API:
	{
		"type": "github",
		"repo": "GovReady/my-modules",
		"path": "modules",
		"auth": { "user": "...", "pw": "..." }
	}

Use `"type": "local"` to load modules from a directory on the local file system. Specify a relative (to working directory when the Django site is launched) or absolute path in `path`.

There are two ways to pull modules from Github:

Use `"type": "git"`, where you specify the `https:...` or `git@...` URL of a git repository in the `url` field and, optionally, a branch name. If the repository requires authentication, you can put an SSH private key such as a [Github deploy key](https://developer.github.com/guides/managing-deploy-keys/) in the `ssh_key` field (paste the whole key using `\n` for newlines, not a filename; `cat .ssh/id_rsa | jq -Rs` will help you turn the SSH key into a JSON string).

Use `"type": "github"`, which uses the Github API and user credentials such as a Github username and a [personal access token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/). Since the `github` method requires user credentials, it should be avoided for production deployments in favor of the `git` method with a deploy key if necessary.

Both git methods have an optional `path` field which lets you choose a directory _within_ the git repository to scan for module YAML files.

### Creating read-only SSH deployment keys

1) Open a terminal.

2) Generate a SSH key pair with the following command:

```
ssh-keygen -t rsa -b 4096 -C "_your-repo-name_-deployment-key" -f ./id_rsa_deploy_key
```

3) When prompted for a passphrase, hit enter to set an empty passphrase.

4) Next, `cat` the contents of the public key file so you can copy the public key to your GitHub repository deployment keys:

```
cat ./id_rsa_deploy_key.pub
```

5) Copy the public key to your clipboard. Then navigate to your your GitHub repo > Settings > Deploy keys. Click the "Add deploy key" button. Paste the content of your public key into the `Key` field. Add a memborable name to the `Title` field like "GovReady Q Deployment Key". 

6) Make the key read only by leaving "Allow write access" field unchecked and click `Add the key` to save the key.

7) Finally, `cat` the contents of the private key file to your terminal while replacing the line breaks. (The line breaks will confuse the json format.) This perl one-liner or the `jq` tool can be used to convert the raw key data into a JSON string:

```
cat ./id_rsa_deploy_key | perl -ne 's/\n/\\n/g; print'
cat ./id_rsa_deploy_key | jq -Rs
```

8) Add the contents of the private key file as the value to the `ssh_key` of your spec file for the Modulesources as specified above.

### App executable content

Apps can contain executable content (some of which is disabled by default):

* JavaScript executed by the client browser contained within page HTML, via module template content.

* JavaScript executed by the client browser served as a static asset and referenced by a `<script>` tag.

* Python scripts executed by the GovReady Q server for `external-function` questions.

Both sources of Javascript execute within the context of pages on the domain that the Q site itself runs on, which means the scripts have access to the page DOM, cookies, localStorage, etc. Server-side Python executes as the local Unix user within the Q Django process. These scripts must only be enabled if they are trusted for these environments.

Javascript static assets and Python scripts (**but not Javascript in module templates** - this is a TODO) are therefore disabled by default. (Javascript static assets are disabled by serving them with an incorrect MIME type. Python assets are not loaded if disabled.)

To enable these scripts, the `Trust javascript assets` flag must be true on the ModuleSource that provides the app. This flag must only be true if any Apps provided by the ModuleSource, including Apps already loaded into Q, are trusted to have executable content that may have as much client or server-side access as the Q instance does itself.


### Updating modules

After making changes to modules or ModuleSources for system modules (like account settings), run `python3 manage.py load_modules` to pull the modules from the sources into the database. This only updates system modules.

Other modules that have already been started as apps will not be updated. But for debugging (only), you can run `python3 manage.py refresh_modules` to update started apps in-place so that you don't have to start an app anew (on the site) each time you make a change to an app.

## Controlling access to apps

Controlling which organizations in a Q deployment can access which apps is done via the ModuleSources table.

The "Available to all" field of ModuleSource, which is on by default, gives all users of all organizations the ability to start an app provided by the ModuleSource. 

If the "Available to all" field is unchecked, then only users within white-listed organizations can start apps provided by the ModuleSource. The white-list is a multi-select box on the ModuleSource page.

Removing access to a ModuleSource does not affect any apps that have already been started by a user.

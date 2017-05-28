# Creating Q Apps

Content in Q is organized around "apps." Apps handle the relationship between parts of a IT system and a compliance framework.

An "app" is a collection of "modules,"" one of which must be named "app." Modules are linear sequence of questions presented to users that produces zero or more output documents. Modules are stored in YAML files. Output documents of various types are supported such as markdown, HTML, and YAML. (See [Schema.md](Schema.md) for documentation on writing modules.)

Aps are loaded into Q from an "app source," which can be a local directory, a Github repository, etc. App sources are linked to a Q deployment through the `ModuleSource` model in the Django admin.

## App Directory Layout

Each Q app is defined by a set of YAML files, an icon, and associated static assets, stored in a directory, e.g.:

    app_name/app.yaml
    app_name/module1.yaml
    app_name/module2.yaml
    app_name/assets/app.png
    app_name/assets/my_image.jpeg

`app.yaml` is a required file in every app which includes app catalog metadata, such as the app's description, as well as module questions which define the layout of the app's main screen once it is started by the user.

Other module YAML file may be includes in the app as well, as needed.

The `assets` subdirectory can contain any static assets that will be served when showing the app's modules for the user, such as images included in document templates. A file typically named `app.png` in the assets directory is the app's icon, which is displayed when browsing the app catalog as well as when the app is used within another app, if `icon: app.png` is specified in `app.yaml`.


## App YAML

The `app.yaml` file that exists in every app serves two purposes:

* It includes app catalog information, i.e. metadata, that will be shown in the app directory, such as the app's short and long description, version number, vendor, etc.
* It also defines a module (see [Schema.md](Schema.md)) which defines the top-level layout of the app. The module may only contain questions whose type are `module` or `module-set`.

The file looks like this:

	id: app
	title: My App
	type: project
	icon: app.png # refers to file in app's assets directory
	protocol: globally_unique_protocol_name # for inner apps only

	catalog:
	  category: Category Name
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


## App Sources

A Q deployment can pull module content from various sources --- including local directories and git repositories --- by creating Module Sources in the Django admin site at [/admin/guidedmodules/modulesource/](http://localhost:8000/admin/guidedmodules/modulesource/). Each Module Source specifies a virtual filesystem from which apps are located.

Whether the source is a local directory or a git repository, the source must have a directory layout in which each app is stored in its own directory. (The directory name becomes an internal name for the app.) For instance:

	app1/app.yaml
	app1/...other_app1_files
	app2/app.yaml
	app2/...other_app2_files
	...

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

7) Finally, `cat` the contents of the private key file to your terminal while replacing the line breaks. (The line breaks will confuse the json format.)

```
cat ./id_rsa_deploy_key | perl -ne 's/\n/\\n/g; print'
```

8) Add the contents of the private key file as the value to the `ssh_key` of your spec file for the Modulesources as specified above.


### Updating modules

After making changes to modules or ModuleSources for system modules (like account settings), run `python3 manage.py load_modules` to pull the modules from the sources into the database. This only updates system modules.

Other modules that have already been started as apps will not be updated. But for debugging (only), you can run `python3 manage.py refresh_modules` to update started apps in-place so that you don't have to start an app anew (on the site) each time you make a change to an app.

## Controlling access to apps

Controlling which organizations in a Q deployment can access which apps is done via the ModuleSources table.

The "Available to all" field of ModuleSource, which is on by default, gives all users of all organizations the ability to start an app provided by the ModuleSource. 

If the "Available to all" field is unchecked, then only users within white-listed organizations can start apps provided by the ModuleSource. The white-list is a multi-select box on the ModuleSource page.

Removing access to a ModuleSource does not affect any apps that have already been started by a user.

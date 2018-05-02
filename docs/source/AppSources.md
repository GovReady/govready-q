# App Sources

GovReady-Q can be configured by an administrator to load compliance apps from one or more sources, which can be local directories or remote git repositories.

When using the Hosted Version of GovReady-Q, GovReady PBC is the administrator. If you are the administrator of an installation of GovReady-Q at your organization, the information below will help you configure the App Sources available to your users.

App Sources are configured in the Django admin at the URL `/admin` on your GovReady-Q domain under `App Sources`:

![App Sources list](assets/appsources_list.png)

Each App Source points GovReady-Q to a directory or repository of compliance apps.

![Example App Source](assets/appsource_git_https.png)

## App Source Slug

The first App Source field is the Slug. The Slug is a short name you assign to the App Source to distinguish it from other App Sources. The Slug is used to form URLs in GovReady-Q's compliance apps catalog, so it may only contain letters, numbers, dashes, underscores, and other URL path-safe characters.

## App Source Type

There are four types of App Sources: local directories, remote git repositories using HTTP which are typically public repositories, remote git repositories using SSH which typically use SSH deploy keys for access, and remote GitHub repositories using a GitHub username and password for access.

### Local Directory

The Local Directory source type directs GovReady-Q to load compliance apps from a directory on the same machine GovReady-Q is running on. (When deploying with Docker, that's on the container filesystem unless a path has been mounted to a volume or to the host machine.)

In the `Path` field, enter the path to a local directory containing compliance apps. This path is expected to contain a sub-directory for each compliance app contained in this source. For instance, if you have this directory layout:

	.
	└── home
	    └── user
	        └── compliance_apps
	            ├── myfirstapp
	            │   └── app.yaml
	            └── mysecondapp
	                └── app.yaml
	
then your Path would be `/home/user/compliance_apps`.

The path can be absolute or relative to the path in which GovReady-Q is installed.

#### Git Repository over HTTPS

The Git Repository over HTTPS source type is for git repositories, such as on GitHub or GitLab, that can be cloned using an HTTPS URL. These repositories are typically public, or in an enterprise environment public within your organization's network.

Paste the HTTPS git clone URL --- such as https://github.com/GovReady/govready-apps-dev --- into the URL field. Here's what that looks like:

![App Source for a public git repository](assets/appsource_git_https.png)

The other fields can be left blank.

The `Path` field optionally specifies a sub-directory within the repository in which the compliance apps are stored if they are not stored in the root of the repository. For instance if the repository has a directory layout similar to:

	.
	└── github.com/organization/repository
	    └── apps
	        ├── myfirstapp
	        │   └── app.yaml
	        └── mysecondapp
	            └── app.yaml

then set the `Path` field to `apps`.

If the compliance apps are not in the repository's default branch (i.e. something other than the typical `master` default branch), then set the `Branch` field to the name of the branch to read the compliance apps from.

You can use HTTPS to access private repositories by placing your username and password or [personal access token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) into the URL, such as:

    https://username:password@github.com/GovReady/govready-apps-dev

Since this requires user credentials, it should be avoided for production deployments in favor of using Git Repository over SSH (see below).

#### Git Repository over SSH

If your git repository is private and accessible using an SSH URL (which typically looks like git@github.com:organization/repository.git) and an SSH public/private keypair, such as with GitHub or GitLab deploy keys, then use the Git Repository over SSH source type.

Create a new SSH key for your GovReady-Q instance to be used as a deploy key:

	ssh-keygen -q -t rsa -b 2048 -N "" -C "_your-repo-name_-deployment-key" -f ./repo_deploy_key

Your GovReady-Q instance will hold the private key half of the newly generated keypair, and your source code control system will hold the public key.

Back in the Django admin, set the Source Type to Git Repository over SSH. Paste the git clone SSH URL into the URL field. Then open the newly generated file `repo_deploy_key` and paste its contents into the SSH Key field. Here's what that looks like:

![App Source for a private git repository](assets/appsource_git_ssh.png)

The other fields can be left blank. `Path` and `Branch` can be set the same as with the Git Repository over HTTPS source type (see above).

Copy the public key in the newly generated file `repo_deploy_key.pub` into the deploy keys section of your source code repository. Here is what that looks like on GitHub:

![Adding a deploy key to GitHub](assets/github_deploy_key_add.png)

Make the key read only by leaving "Allow write access" field unchecked and click `Add the key` to save the key.

#### GitHub Repository using the GitHub API

This source type can be used to access private GitHub repositories using a GitHub username and password or a username and [personal access token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/).

Set the `Repository` field to the organization name and repository name, separated by a slash, as in the repository's URL following `github.com/`. In `Other Parameters`, paste a small YAML-formatted document holding a GitHub username and password or username and personal access token, formatted as follows:

	auth:
	  user: 'myusername'
	  pw: 'mypassword'

The other fields can be left blank. `Branch` can be set the same as with the Git Repository over HTTPS source type (see above).

Since this source type requires user credentials, it should be avoided for production deployments in favor of using Git Repository over SSH.


## Controlling access to apps

Controlling which organizations in a Q deployment can access which apps is done via the App Sources table.

The "Available to all" field of App Source, which is on by default, gives all users of all organizations the ability to start an app provided by the App Source. 

If the "Available to all" field is unchecked, then only users within white-listed organizations can start apps provided by the App Source. The white-list is a multi-select box on the App Source page.

Removing access to a App Source does not affect any apps that have already been started by a user.


### App executable content

Apps can contain executable content (some of which is disabled by default):

* JavaScript executed by the client browser contained within page HTML, via module template content.

* JavaScript executed by the client browser served as a static asset and referenced by a `<script>` tag.

Both sources of Javascript execute within the context of pages on the domain that the Q site itself runs on, which means the scripts have access to the page DOM, cookies, localStorage, etc. These scripts must only be enabled if they are trusted for these environments.

Javascript static assets  (**but not Javascript in module templates** - this is a TODO) are therefore disabled by default. (Javascript static assets are disabled by serving them with an incorrect MIME type.)

To enable these scripts, the `Trust assets` flag must be true on the App Source that provides the app. This flag must only be true if any Apps provided by the App Source, including Apps already loaded into Q, are trusted to have executable content that may have as much client or server-side access as the Q instance does itself.
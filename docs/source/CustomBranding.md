Applying Custom Organization Branding
=====================================

The look and feel of GovReady-Q can be customized a bit by overriding the Django templates that are used to construct the site's pages and by serving additional static assets.

Custom branding can contain static assets (such as a logo image) and HTML template overrides. Branding is packaged into a directory with a particular directory layout and some Python boilerplate code that allows GovReady-Q to find the branding files. The directory is placed inside the main GovReady-Q directory, and an application setting is used to activate it.

Before setting out to create custom branding, make sure you have GovReady-Q [set up for development on your workstation](deploy_local_dev.html). You'll need a working setup of GovReady-Q to create the branding directory and to test your changes.

## Creating the branding directory

Custom branding is packaged inside what Django confusingly calls an [application](https://docs.djangoproject.com/en/2.1/ref/applications/), but it is just a packaged sub-component of a website. To create a new branding package directory, change to the directory where you have GovReady-Q set up. Then run:

```sh
python3 manage.py startapp sample_branding
```

This command creates a new directory called `sample_branding` with Python boilerplate code to make it a valid Django "application."

Make directories for storing the custom static assets and templates:

```sh
mkdir sample_branding/static
mkdir sample_branding/templates
```

## Activate the branding package

Next, let your development installation of GovReady-Q know that you want to use the custom branding package. In your `local/environment.json` file, add a setting named `branding` and set it to the name of the custom branding package directory.

```sh
  "branding": "sample_branding",
```

See [Environment Settings](Environment.html) for more information about the `local/environment.json` file. Note that for the file to be valid JSON the last setting cannot have a trailing comma.

## Overriding templates

Any of the templates that make up GovReady-Q's frontend can be overridden. The full list of templates can be browsed in GovReady-Q's GitHub repository at

https://github.com/GovReady/govready-q/tree/master/templates

Start by trying to override the `navbar.html` template, which is inserted at the top of every page. Use your favorite text editor to create a file at `sample_branding/templates/navbar.html`. Copy the content of GovReady-Q's stock `navbar.html` from https://github.com/GovReady/govready-q/blob/master/templates/navbar.html into it. (GitHub's "Raw" button is handy for getting a clean version to save or copy/paste.)

At the bottom of the file, add some custom HTML, such as:

```html
<div>
  <b>Welcome to my organization&rsquo;s custom site!</b>
</div>
```

Start GovReady-Q on your workstation (see the [development docs](deploy_local_dev.html)) and visit a page. You should see your new content below the navbar at the top of every page.

## Adding custom CSS

You can also add a custom CSS stylesheet to your branded GovReady-Q by taking the following steps:

a) Add the CSS file as a static asset.
b) Insert a `<link rel="stylesheet" href="...">` tag into the `<head>` section of each page's HTML by overriding the `head.html` template.

To create the static asset, make a new file named `sample_branding/static/custom.css`. Let's say you want to make the background color of each page red. The file should contain:

```css
body {
	background: red !important;
}
```

Then override the `head.html` template. GovReady-Q's base for `head.html` is empty --- its purpose is only to allow you to add to the `<head>` element. So create a new file at `sample_branding/templates/head.html` and put in it:

```html
{% load static %}
<link rel="stylesheet" href="{% static "custom.css" %}">
```

See the [Django documentation for static files](https://docs.djangoproject.com/en/2.1/howto/static-files/) for more information about the `static` template tag.

Open any page in your locally running GovReady-Q and you should see that the background color of every page has changed.

## Keeping your templates up to date

With each new released version of GovReady-Q, there is the possibility that the stock templates have changed. Some changes may require you to re-engineer your template overrides to preserve functionality.

## Creating a custom Docker image

If your organization is deploying GovReady-Q using Docker, you will need to embed your custom branding package within a Docker image. You have two options:

1. Modify GovReady-Q's stock Dockerfile, i.e. the one in GovReady-Q's source code, to add and activate your branding package and then _build your own GovReady-Q Docker image_ from the GovReady-Q source files that you cloned from GitHub.
2. Make your own Dockerfile that _uses a released GovReady-Q image as its parent image_ and adds to it just the steps needed to add and activate your branding package.

### Creating your own Dockerfile that uses a released GovReady-Q image as its parent image

We recommend method 2. To create your own Dockerfile that uses a released GovReady-Q image as its parent image, create a new `Dockerfile` in your branding package directory, e.g. a new file named `Dockerfile` in the `sample_branding` directory you created earlier.

Then choose which parent image you will use from the available [GovReady-Q tags](https://hub.docker.com/r/govready/govready-q/tags). Each tag corresponds to a release version. Your Dockerfile begins with a `FROM` line that combines `govready/govready-q:` with the tag name you choose. In this example we use the `latest` tag which is an alias for the most recent version of GovReady-Q:

```Dockerfile
FROM govready/govready-q:latest
```

The subsequent commands in your Dockerfile configures the container, picking up where the parent image's Dockerfile leaves off. For more information about the parent image, refer to [GovReady-Q's Dockerfile on GitHub](https://github.com/GovReady/govready-q/blob/master/Dockerfile).

Your Dockerfile's next step is to add your branding package into the image in a directory named `branding`:

```Dockerfile
RUN mkdir branding
COPY . branding
```

Finally, you'll need some commands to adjust permissions, to activate the branding package when GovReady-Q starts, and to prepare the static assets to be served. The complete Dockerfile should look like this:

```Dockerfile
# Build an image on top of the stock GovReady-Q image.
FROM govready/govready-q:latest

# The parent Dockerfile ends with 'USER application' to run the
# container as a non-privileged user. But we need to go back to
# root to add additional files and then switch back to the non-
# root user at the end.
USER root

# Copy our public app files into place.
RUN mkdir branding
COPY . branding

# Activate the branding package. The environment variable is read
# by dockerfile_exec.sh in the GovReady-Q parent image. And modifying
# /tmp/environment.json is necessary at this step so that collectstatic
# picks it up below.
ENV BRANDING branding
RUN sed -i "s/}/,\"branding\": \"branding\" }/" /tmp/environment.json

# Flatten static files. The base image did it once, but we may have
# added new static files so we must do it again.
RUN python3.6 manage.py collectstatic --noinput

# Run the container's process zero as this user --- see above.
USER application

# Check that everything looks good.
RUN python3.6 manage.py check
```

Finally you can build and test your custom image.

### Building your docker image

If you were in the GovReady-Q sources directory, move into your branding package directory:

```bash
cd sample_branding
```

Then fetch the parent image and build your image:

```bash
docker image pull govready/govready-q:latest
docker image build --tag myorg/govready-q-branded:latest .
```

(Substitute the right tag depending on the tag you chose for the `FROM` line in your Dockerfile.)

Test that your image works by launching a new container based on your image:

```bash
docker container run --rm -it -p 127.0.0.1:8000:8000 myorg/govready-q-branded:latest
```

Once GovReady-Q is running in the container, visit it at `http://localhost:8000`. Use CTRL+C in the console to terminate and destroy the test container running your image.

For more about running GovReady-Q with Docker, see [Deploying with Docker](deploy_docker.html).
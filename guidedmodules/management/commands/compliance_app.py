from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from guidedmodules.models import AppSource

import os, os.path, shutil

import rtyaml

# ./manage.py compliance_app   # lists available app sources
# ./manage.py compliance_app mysource --path path/to/apps # creates a new local AppSource named mysource
# ./manage.py compliance_app mysource myapp # creates a new app at path/to/apps/myapp

class Command(BaseCommand):
    help = 'Creates a new compliance app. Lists available appsource names if no command-line arguments are given.'

    def add_arguments(self, parser):
        parser.add_argument('appsource', nargs="?", type=str)
        parser.add_argument('--path', nargs="?", type=str)
        parser.add_argument('appname', nargs="?", type=str)

    def handle(self, *args, **options):
        if not options["appsource"]:
            # Show valid appsources.
            print("Specify one of the following app sources:")
            for appsrc in AppSource.objects.all():
                if appsrc.spec["type"] == "local" and appsrc.spec.get("path"):
                    print(appsrc.namespace, "(path: " + appsrc.spec["path"] + ")")
            return

        elif options["path"]:
            if options["appname"]:
                print("You cannot use --path together with an appname.")
                return

            # Make directory if it doesn't exist.
            os.makedirs(options["path"], exist_ok=True)

            # Create a new AppSource.
            appsrc = AppSource.objects.create(
                namespace=options["appsource"],
                spec={ "type": "local", "path": options["path"] }
            )

            print("Created new AppSource", appsrc, "using local path", options["path"])

        
        elif not options["appname"]:
            print("You must specify an app name, which should be a valid directory name (i.e. no spaces), or  or --path to create a new AppSource.")

        else:
            # Ok do the real work.

            appsrc = AppSource.objects.get(namespace=options["appsource"])

            # Do we have a path?
            if not appsrc.spec.get("path"):
                print("AppSource does not have a local path specified!")
                return

            # What's the path to the app?
            path = os.path.join(appsrc.spec["path"], options["appname"])

            # Does this app already exist?
            if os.path.exists(path):
                print("An app with that name already exists.")
                return

            # Copy stub files.
            guidedmodules_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            shutil.copytree(os.path.join(guidedmodules_path, "stub_app"), path, copy_function=shutil.copy)

            # Edit the app title.
            with open(os.path.join(path, "app.yaml"), "r+") as f:
                app = rtyaml.load(f.read())

                # Update info
                app['title'] = options["appname"]

                # Write out.
                f.seek(0)
                f.truncate()
                f.write(rtyaml.dump(app))

            # Create a unique icon for the app and delete the existing app icon
            # svg file that we know is in the stub.
            from mondrianish import generate_image
            colors = ("#FFF8F0", "#FCAA67", "#7DB7C0", "#932b25", "#498B57")
            with open(os.path.join(path, "assets", "app.png"), "wb") as f:
                generate_image("png", (128, 128), 3, colors, f)
            os.unlink(os.path.join(path, "assets", "app.svg"))

            # Which AppSource is used?
            print("Created new app in AppSource", appsrc, "at", path)


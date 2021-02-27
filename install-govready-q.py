#!/usr/bin/env python3

################################################################
#
# install-govready-q.py - Quickly set up a new GovReady-Q instance
#   from a freshly-cloned repository.
#
# Usage: install-govready-q.py [--help] [--non-interactive] [--verbose]
#
# Optional arguments:
#   -h, --help             show this help message and exit
#   -n, --non-interactive  run without terminal interaction
#   -u, --user             do pip install with --user flag
#   -v, --verbose          output more information
#
################################################################

# parse command-line arguments
import argparse

# system stuff
import os
import signal
import subprocess
import sys

# JSON handling
import json

# Default constants
GOVREADYURL = "http://localhost:8000"
SPACER = "..."

# Gracefully exit on control-C
signal.signal(signal.SIGINT, lambda signal_number, current_stack_frame: sys.exit(0))

# define a fatal error handler
class FatalError(Exception):
    pass

# Set up argparse
def init_argparse():
    parser = argparse.ArgumentParser(description='Quickly set up a new GovReady-Q instance from a freshly-cloned repository.')
    parser.add_argument('--non-interactive', '-n', action='store_true', help='run without terminal interaction')
    parser.add_argument('--user', '-u', action='store_true', help='do pip install with --user flag')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='output more information')
    return parser

def check_has_command(command_array):
    try:
        p = subprocess.run(command_array, capture_output=True)
        return True
    except FileNotFoundError as err:
        return False

def create_environment_json(path):
    import secrets
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = ''.join(secrets.choice(alphabet) for i in range(50))
    # NOTE: `environment` here refers to locally-created environment data object and not OS-level environment variables
    environment = {
	"govready-url": GOVREADYURL,
	"static": "static_root",
	"secret-key": secret_key,
        "debug": True
    }
    with open(path, 'w') as f:
        f.write(json.dumps(environment, sort_keys=True, indent=2))

def main():
    try:
        argparser = init_argparse();
        args = argparser.parse_args();
            
        # check for python3 and pip3 (and not 2 or e.g. 'python3.8')
        if not check_has_command(['python3', '--version']):
            raise FatalError("The 'python3' command is not available.")
        if not check_has_command(['pip3', '--version']):
            raise FatalError("The 'pip3' command is not available.")

        # print mode of interactivity
        if args.non_interactive:
            print("Installing GovReady-Q in non-interactive mode...")
        else:
            print("Installing GovReady-Q in interactive mode (default)...")

        # pip install basic requirements
        if args.user:
            subprocess.run(['pip3', 'install', '--user', '-r', 'requirements.txt'])
        else:
            subprocess.run(['pip3', 'install', '-r', 'requirements.txt'])

        # print spacer
        print(SPACER)

        # create the local/environment.json file, if it is missing (it generally will be)
        # NOTE: `environment` here refers to locally-created environment data object and not OS-level environment variables
        environment_path = 'local/environment.json'
        if os.path.exists(environment_path):
            # confirm that environment.json is JSON
            try:
                environment = json.load(open(environment_path))
                print("environment.json file already exists, proceeding")
            except json.decoder.JSONDecodeError as e:
                print("'{}' is not in JSON format:".format(environment_path))
                print(">>>>>>>>>>")
                print(open(environment_path).read())
                print("<<<<<<<<<<")
                raise FatalError("'{}' is not in JSON format.".format(environment_path))
        else:
            print("creating DEV {} file".format(environment_path))
            create_environment_json(environment_path)

        # debugging STOP
        print("got here")
        sys.exit(0)

        # retrieve static assets
        subprocess.run(['./fetch-vendor-resources.sh'])

        # collect files into static directory
        if args.non_interactive:
            subprocess.run(['./manage.py', 'collectstatic', '--no-input'])
        else:
            subprocess.run(['./manage.py', 'collectstatic'])

    except FatalError as err:
        print("\n\nFatal error, exiting: {}\n".format(err));
        sys.exit(1)

if __name__ == "__main__":
    exit(main())

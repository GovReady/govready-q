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

# Define a fatal error handler
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
    "test_visible": False,
    "debug": True
    }
    # Create local directory
    if not os.path.exists('local'):
        os.makedirs('local')
    #Create local/envionment.json file
    with open(path, 'w') as f:
        f.write(json.dumps(environment, sort_keys=True, indent=2))

def main():
    print(">>>>>>>>>> Welcome to the GovReady-Q Installer <<<<<<<<<\n")
    print("Testing environment...\n")

    # Test version of Python
    ver = sys.version_info
    print("GovReady-Q Installer running with Python {}.{}.{}".format(ver[0],ver[1],ver[2]))

    if sys.version_info >= (3, 8):
        print("√ Python version is >= 3.8.")
    else:
        print("! Python version is < 3.8.")
        print("GovReady-Q is best run with Python 3.8 or higher.")
        print("It is STRONGLY encouraged to run GovReady-Q inside a Python 3.8 or higher.")
        reply = input("Continue install with Python {}.{}.{} (y/n)? ".format(ver[0],ver[1],ver[2]))
        if len(reply) == 0 or reply[0].lower() != "y":
            print("Install halted.")
            sys.exit(0)

    argparser = init_argparse();
    args = argparser.parse_args();

    # Check if inside a virtual environment
    if sys.prefix != sys.base_prefix:
        print("√ Installer is running inside a virtual Python environment.\n")
    else:
        print("! Installer is not running inside a virtual Python environment.")
        print("It is STRONGLY encouraged to run GovReady-Q inside a Python virtual environment.")
        reply = input("Continue install outside of virtual environment (y/n)? ")
        if len(reply) == 0 or reply[0].lower() != "y":
            print("Install halted.")
            sys.exit(0)

    # Check for python3 and pip3 (and not 2 or e.g. 'python3.8')
    if not check_has_command(['python3', '--version']):
        raise FatalError("The 'python3' command is not available.")
    if not check_has_command(['pip3', '--version']):
        raise FatalError("The 'pip3' command is not available.")

    # Print mode of interactivity
    if args.non_interactive:
        print("Installing GovReady-Q in non-interactive mode...")
    else:
        print("Installing GovReady-Q in interactive mode (default)...")

    # pip install basic requirements
    if args.user:
        subprocess.run(['pip3', 'install', '--user', '-r', 'requirements.txt'])
    else:
        subprocess.run(['pip3', 'install', '-r', 'requirements.txt'])

    # Print spacer
    print(SPACER)

    # Create the local/environment.json file, if it is missing (it generally will be)
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

    # Configure database
    try:
        subprocess.run(["./manage.py", "migrate"], capture_output=False)
    except FatalError as err:
        print("\n\nFatal error, exiting: {}\n".format(err));
        sys.exit(1)

    # Load modules
    try:
        subprocess.run(["./manage.py", "load_modules"], capture_output=False)
    except FatalError as err:
        print("\n\nFatal error, exiting: {}\n".format(err));
        sys.exit(1)

    # Run first_run non-interactive
    try:
        subprocess.run(["./manage.py", "first_run", "--non-interactive"], capture_output=False)
    except FatalError as err:
        print("\n\nFatal error, exiting: {}\n".format(err));
        sys.exit(1)

    # Run first_run interactive
    # try:
    #     subprocess.run(["./manage.py", "first_run"], capture_output=False)
    # except FatalError as err:
    #     print("\n\nFatal error, exiting: {}\n".format(err));
    #     sys.exit(1)

    # Retrieve static assets
    try:
        subprocess.run(['./fetch-vendor-resources.sh'])
    except FatalError as err:
        print("\n\nFatal error, exiting: {}\n".format(err));
        sys.exit(1)

    # Collect files into static directory
    try:
        if args.non_interactive:
            subprocess.run(['./manage.py', 'collectstatic', '--no-input'])
        else:
            subprocess.run(['./manage.py', 'collectstatic'])
    except FatalError as err:
        print("\n\nFatal error, exiting: {}\n".format(err));
        sys.exit(1)

    # # Debugging STOP
    # print("got here")
    # sys.exit(0)

if __name__ == "__main__":
    exit(main())

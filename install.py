#!/usr/bin/env python3

################################################################
#
# install.py - Quickly set up a new GovReady-Q instance
#   from a freshly-cloned repository.
#
# Usage: install.py [--help] [--non-interactive] [--verbose]
#
# Optional arguments:
#   -h, --help             show this help message and exit
#   -n, --non-interactive  run without terminal interaction
#   -t, --timeout          seconds to allow external programs to run
#   -u, --user             do pip install with --user flag
#   -v, --verbose          output more information
#
################################################################

# Note: we use print("foo") ; sys.stdout.flush() instead of print("", flush=True)
# to avoid a syntax error crash if run under Python 2.

# parse command-line arguments
import argparse

# system stuff
import os
import platform
import re
import signal
import subprocess
import sys
import time
from subprocess import PIPE

# JSON handling
import json

# Default constants
GOVREADYURL = "http://localhost:8000"
SPACER = "\n====\n"

# Gracefully exit on control-C
signal.signal(signal.SIGINT, lambda signal_number, current_stack_frame: sys.exit(0))


# Define a fatal error handler
class FatalError(Exception):
    pass


# Define a halted error handler
class HaltedError(Exception):
    pass


# Define a non-zero return code error handler
class ReturncodeNonZeroError(Exception):
    def __init__(self, completed_process, msg=None):
        if msg is None:
            # default message if none set
            msg = "An external program or script returned an error."
        super(ReturncodeNonZeroError, self).__init__(msg)
        self.completed_process = completed_process


# Set up argparse
def init_argparse():
    parser = argparse.ArgumentParser(
        description='Quickly set up a new GovReady-Q instance from a freshly-cloned repository.')
    parser.add_argument('--non-interactive', '-n', action='store_true', help='run without terminal interaction')
    parser.add_argument('--timeout', '-t', type=int, default=120,
                        help='seconds to allow external programs to run (default=120)')
    parser.add_argument('--user', '-u', action='store_true', help='do pip install with --user flag')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='output more information')
    parser.add_argument('--docker', '-d', action='store_true', help='runs with docker installation')
    return parser


################################################################
#
# helpers
#
################################################################

def run_optionally_verbose(args, timeout, verbose_flag):
    if verbose_flag:
        import time
        start = time.time()
        print(f"Executing: {args}")
        p = subprocess.run(args, timeout=timeout)
        print("Elapsed time: {:1f} seconds.".format(time.time() - start))
    else:
        p = subprocess.run(args, timeout=timeout, stdout=PIPE, stderr=PIPE)
    return p


def check_has_command(command_array):
    try:
        # hardcode timeout to 5 seconds; if checking command takes longer than that, something is really wrong
        p = subprocess.run(command_array, timeout=5, stdout=PIPE, stderr=PIPE)
        return True
    except FileNotFoundError as err:
        return False


# checks if a package is out of date
# if okay, returns (True, None, None)
# if out of date, returns (False, current_version, latest_version)
# N.B., this routine will return okay if the package is not installed
def check_package_version(package_name):
    p = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated', '--format', 'json'], stdout=PIPE, stderr=PIPE)
    packages = json.loads(p.stdout.decode('utf-8'))
    for package in packages:
        if package['name'] == package_name:
            return False, package['version'], package['latest_version']
    return True, None, None


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
    "debug": True,
    "session_security_expire_at_browser_close" : True,
    "session_security_warn_after" : 1200,
    "session_security_expire_after" : 1800
    }
    # Create local directory
    if not os.path.exists('local'):
        os.makedirs('local')
    # Create local/envionment.json file
    with open(path, 'w') as f:
        f.write(json.dumps(environment, sort_keys=True, indent=2))


def main():
    print(">>>>>>>>>> Welcome to the GovReady-Q Installer <<<<<<<<<\n")

    try:
        # Collect command line arguments, print help if necessary
        argparser = init_argparse();
        args = argparser.parse_args();

        python_manage = ['./manage.py']
        if args.docker:
            python_manage = [sys.executable, "manage.py"]
        elif os.name == 'nt':
            python_manage = [sys.executable, 'manage.py']

        print("Testing environment...\n")

        # Print machine information
        print("Platform is {} version {} running on {}.".format(platform.system(), platform.release(), platform.machine()))

        # Print spacer
        print(SPACER)

        # Test version of Python
        ver = sys.version_info
        print("Python version is {}.{}.{}.".format(ver[0], ver[1], ver[2]))

        if sys.version_info >= (3, 6):
            print("+ Python version is >= 3.6.")
        else:
            print("! Python version is < 3.6.")
            print("GovReady-Q is best run with Python 3.6 or higher.")
            print("It is STRONGLY encouraged to run GovReady-Q with Python 3.8 or higher.")
            if args.non_interactive:
                reply = ''
            else:
                reply = input("Continue install with Python {}.{}.{} (y/n)? ".format(ver[0], ver[1], ver[2]))
            if len(reply) == 0 or reply[0].lower() != "y":
                raise HaltedError("Python version is < 3.8")

        # Print spacer
        print(SPACER)

        # Check if inside a virtual environment
        if not args.docker:
            print("Check for virtual Python environment.")
            if sys.prefix != sys.base_prefix:
                print("+ Installer is running inside a virtual Python environment.")
            else:
                print("! Installer is not running inside a virtual Python environment.")
                print("It is STRONGLY encouraged to run GovReady-Q inside a Python virtual environment.")
                if args.non_interactive:
                    reply = ''
                else:
                    reply = input("Continue install outside of virtual environment (y/n)? ")
                if len(reply) == 0 or reply[0].lower() != "y":
                    raise HaltedError("Installer is not running inside a virtual Python environment")

        # Print spacer
        print(SPACER)

        # Check for python3 and pip3 (and not 2 or e.g. 'python3.8')
        print("Confirming python3 and pip3 commands are available...")
        sys.stdout.flush()
        if not check_has_command(['python3', '--version']):
            raise FatalError("The 'python3' command is not available.")
        if not check_has_command(['pip3', '--version']):
            raise FatalError("The 'pip3' command is not available.")
        print("... done confirming python3 and pip3 commands are available.")
        sys.stdout.flush()

        # Print spacer
        print(SPACER)

        # Check for updated pip
        print("Check that pip is up to date.")
        pip_up_to_date, pip_current, pip_latest = check_package_version('pip')
        if pip_up_to_date:
            print("+ pip is up to date.")
        else:
            print("! pip is not the latest version ({} vs. {}).".format(pip_current, pip_latest))
            print("It is STRONGLY encouraged to ensure pip is updated before continuing, or non-obvious errors may occur.")
            if args.non_interactive:
                reply = ''
            else:
                reply = input("Continue install with outdated pip (y/n)? ")
            if len(reply) == 0 or reply[0].lower() != "y":
                raise HaltedError(
                    "pip is not up to date ({} vs. {}).\n\nSuggested fix: Run 'pip install --upgrade pip'".format(
                        pip_current, pip_latest))

        # Print spacer
        print(SPACER)

        # Print mode of interactivity
        if args.non_interactive:
            print("Installing/updating GovReady-Q in non-interactive mode.")
        else:
            print("Installing/updating GovReady-Q in interactive mode.")

        # Print spacer
        print(SPACER)

        # Briefly sleep in verbose mode so user can glance at output.
        time.sleep(3) if args.verbose else time.sleep(0)

        # pip install basic requirements
        print("Installing Python libraries via pip (this may take a while)...")
        sys.stdout.flush()
        if args.user:
            pip_install_command = ['pip3', 'install', '--user', '-r', 'requirements.txt']
        else:
            pip_install_command = ['pip3', 'install', '-r', 'requirements.txt']
        if args.docker:
            pip_install_command.append('--ignore-installed')

        p = run_optionally_verbose(pip_install_command, args.timeout, args.verbose)
        if p.returncode != 0:
            raise ReturncodeNonZeroError(p)
        print("... done installing Python libraries via pip.")
        sys.stdout.flush()

        # Print spacer
        print(SPACER)

        # # Retrieve static assets
        if args.docker:
            print("Fetching static resource files from Internet...")
            sys.stdout.flush()
            p = run_optionally_verbose(['./fetch-vendor-resources.sh'], args.timeout, args.verbose)
            if p.returncode != 0:
                raise ReturncodeNonZeroError(p)
            print("... done fetching resource files from Internet.")
            sys.stdout.flush()

            # Print spacer
            print(SPACER)

        # Create the local/environment.json file, if it is missing (it generally will be)
        # NOTE: `environment` here refers to locally-created environment data object and not OS-level environment variables
        print("Creating local/environment.json file...")
        sys.stdout.flush()
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
            create_environment_json(environment_path)
        print("... done creating local/environment.json file.")
        sys.stdout.flush()

        # Print spacer
        print(SPACER)

        # Configure database (migrate, load_modules)
        print("Initializing/migrating database...")
        sys.stdout.flush()
        print(python_manage)
        p = run_optionally_verbose([*python_manage, "migrate"], args.timeout, args.verbose)
        if p.returncode != 0:
            raise ReturncodeNonZeroError(p)
        p = run_optionally_verbose([*python_manage, "load_modules"], args.timeout, args.verbose)
        if p.returncode != 0:
            raise ReturncodeNonZeroError(p)
        print("... done initializing/migrating database.")
        sys.stdout.flush()

        # Print spacer
        print(SPACER)

        # Collect files into static directory
        print("Collecting files into static directory...")
        sys.stdout.flush()
        if args.non_interactive:
            p = run_optionally_verbose([*python_manage, 'collectstatic', '--no-input'], args.timeout, args.verbose)
            if p.returncode != 0:
                raise ReturncodeNonZeroError(p)
        else:
            p = run_optionally_verbose([*python_manage, 'collectstatic', '--no-input'], args.timeout, args.verbose)
            if p.returncode != 0:
                raise ReturncodeNonZeroError(p)
        print("... done collecting files into static directory.")
        sys.stdout.flush()

        # Print spacer
        print(SPACER)

        # Run first_run non-interactively
        print("Setting up system and creating Administrator user if none exists...")
        sys.stdout.flush()
        p = subprocess.run([*python_manage, "first_run", "--non-interactive"], timeout=args.timeout, stdout=PIPE,
                           stderr=PIPE)
        if p.returncode != 0:
            raise ReturncodeNonZeroError(p)
        if args.verbose:
            print(p.stdout.decode('utf-8'), p.stderr.decode('utf-8'))
        # save admin account details
        admin_details = ''
        if p.stdout:
            m1 = re.search('\n(Created administrator account.+)\n', p.stdout.decode('utf-8'))
            m2 = re.search('\n(Skipping create admin account.+)\n', p.stdout.decode('utf-8'))
            m3 = re.search('\n(\[INFO\] Superuser.+)\n', p.stdout.decode('utf-8'))
            if m1:
                admin_details = m1.group(1)
            elif m2:
                admin_details = "Administrator account(s) previously created."
            elif m3:
                admin_details = "Administrator account(s) previously created."
            else:
                admin_details = "Administrator account details not found."
        print("... done setting up system and creating Administrator user.")
        sys.stdout.flush()

        # Print spacer
        print(SPACER)

        # Load GovReady sample SSP
        print("Setting up GovReady-Q sample project if none exists...")
        sys.stdout.flush()
        p = run_optionally_verbose([*python_manage, "load_govready_ssp"], args.timeout, args.verbose)
        if p.returncode != 0:
            raise ReturncodeNonZeroError(p)
        print("... done setting up GovReady-Q sample project.")
        sys.stdout.flush()

        # Print spacer
        print(SPACER)

        print("""\

***********************************
* GovReady-Q Server configured... *
***********************************

To start GovReady-Q, run:
    ./manage.py runserver
""")

        if len(admin_details):
            if "Created administrator account" in admin_details:
                print("Log in using the administrator credentials printed below.\n\nWRITE THIS DOWN:\n")
            print(admin_details, "\n")

        print("When GovReady-Q is running, visit http://localhost:8000/ with your web browser.\n")

    except ReturncodeNonZeroError as err:
        p = err.completed_process
        sys.stderr.write("\n\nFatal error, exiting: external program or script {} returned error code {}.\n\n".format(p.args,
                                                                                                                      p.returncode))
        # diagnose stdout and stdout to see if we can find an obvious problem
        # (add more checks here as appropriate)
        # check for missing Xcode Command Line Tools (macOS)
        if p.stderr and 'xcrun: error: invalid active developer path (/Library/Developer/CommandLineTools), missing xcrun at: /Library/Developer/CommandLineTools/usr/bin/xcrun' in p.stderr.decode(
                'utf-8'):
            sys.stderr.write("Suggested fix (see documentation): You need to do 'xcode-select --install'.\n\n")
        sys.exit(1)

    except subprocess.TimeoutExpired as err:
        sys.stderr.write(
            "\n\nFatal error, exiting: external program or script {} took longer than {:.1f} seconds.\n\n".format(err.cmd,
                                                                                                                  err.timeout))
        sys.stderr.write("Suggested fix: run again with '--timeout {}'.\n\n".format(max(args.timeout + 120, 600)))
        sys.exit(1)

    except HaltedError as err:
        sys.stderr.write("\n\nInstall halted because: {}.\n\n".format(err));
        sys.exit(1)

    except FatalError as err:
        sys.stderr.write("\n\nFatal error, exiting: {}.\n\n".format(err));
        sys.exit(1)

    # catch all errors
    except Exception as err:
        sys.stderr.write(
            '\n\nFatal error, exiting: unrecognized error on line {}, "{}".\n\n'.format(sys.exc_info()[2].tb_lineno, err));
        sys.exit(1)


if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python

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
#   -v, --verbose          output more information
#
################################################################

# parse command-line arguments
import argparse

# system stuff
import sys
import signal
import subprocess

# JSON handling
import json

# Gracefully exit on control-C
signal.signal(signal.SIGINT, lambda signal_number, current_stack_frame: sys.exit(0))

# define a fatal error handler
class FatalError(Exception):
    pass

# Set up argparse
def init_argparse():
    parser = argparse.ArgumentParser(description='Quickly set up a new GovReady-Q instance from a freshly-cloned repository.')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='output more information')
    parser.add_argument('--non-interactive', '-n', action='store_true', help='run without terminal interaction')
    return parser

def main():
    try:
        argparser = init_argparse();
        args = argparser.parse_args();
            
    except FatalError as err:
        print("\n\nFatal error, exiting: {}\n".format(err));
        sys.exit(1)

if __name__ == "__main__":
    exit(main())

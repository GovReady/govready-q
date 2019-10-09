#!/bin/bash

set -euf -o pipefail # abort script on error

python3.6 manage.py add_data $@

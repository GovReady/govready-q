#!/bin/bash

# use 'head' to suppress display of actual processes, which might expose sensitive information
if [ "$(uname)" == "Darwin" ]; then
    top -l 1 | head -10
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    top -n 1 -b | head -5
else
    echo "check-system.sh is not supported on this system"
fi


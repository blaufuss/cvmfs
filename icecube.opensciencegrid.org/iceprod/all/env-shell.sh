#!/bin/sh

if [ -z "$1" ]
    then # user did not specify a shell
    NEW_SHELL=$SHELL
    # only exit if no shell specified on command line *and* env already loaded
    if [ -n "$I3_SHELL" ]
        then
        echo "****************************************************************"
        echo "You already have an IceCube CVMFS environment loaded."
        echo "Please exit the current shell and re-run $0 from a clean shell."
        echo "****************************************************************"
        echo "Environment not (re)loaded."
        exit 2
    fi
else
    NEW_SHELL=$1
    shift
    ARGV="$@"
fi

DIR=$(echo "${0%/*}")
BASE=$(cd "$DIR" && echo "$(pwd -L)")
eval `${BASE}/setup.sh`

if [ -z "$ARGV" ]; then
    echo "Loaded IceProd env"
fi

$NEW_SHELL "$@"

if [ -z "$ARGV" ]; then
    echo "Exited IceProd env"
fi

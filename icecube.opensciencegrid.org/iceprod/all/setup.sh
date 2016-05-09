#!/bin/sh

# from bash or tcsh, call this script as:
# eval `/cvmfs/icecube.opensciencegrid.org/iceprod/current/setup.sh`

# This is here since readlink -f doesn't work on Darwin
DIR=$(echo "${0%/*}")
ICEPRODBASE=$(cd "$DIR" && echo "$(pwd -L)")

# load IceCube environmentOLD_IFS=$IFS
SETUP=`$ICEPRODBASE/../../py2-v2/setup.sh`
IFS=';'
VARS=""
for x in $SETUP; do
    IFS='='
    for y in $x; do
        z=`echo $y|sed 's/export//g'|tr -d ' \n'`
        if [ "x${VARS}" = "x" ]; then
            VARS="$z"
        else
            VARS="${VARS} $z"
        fi
        break
    done
    IFS=';'
done
eval $SETUP

ICEPRODROOT=$ICEPRODBASE/$OS_ARCH

PATH=$ICEPRODROOT/bin:$PATH

PKG_CONFIG_PATH=$ICEPRODROOT/lib/pkgconfig:$PKG_CONFIG_PATH
LD_LIBRARY_PATH=$ICEPRODROOT/lib:$LD_LIBRARY_PATH
PYTHONPATH=$ICEPRODROOT/lib/python2.7/site-packages:$PYTHONPATH
MANPATH=$ICEPRODROOT/man:$ICEPRODROOT/share/man:$MANPATH

VARS="${VARS} ICEPRODBASE ICEPRODROOT"

IFS=' '
for name in ${VARS}
do
  eval VALUE=\$$name
  case ${SHELL##*/} in
    tcsh)
        echo 'setenv '$name' '\"$VALUE\"' ;' ;;
    csh)
        echo 'setenv '$name' '\"$VALUE\"' ;' ;;
    *)
        echo 'export '$name=\"$VALUE\"' ;' ;;
  esac
done

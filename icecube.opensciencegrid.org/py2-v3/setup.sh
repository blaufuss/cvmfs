#!/bin/sh

# from bash or tcsh, call this script as:
# eval `/cvmfs/icecube.opensciencegrid.org/setup.sh`

# This is here since readlink -f doesn't work on Darwin
DIR=$(echo "${0%/*}")
SROOTBASE=$(cd "$DIR" && echo "$(pwd -L)")

. $SROOTBASE/os_arch.sh

SROOT=$SROOTBASE/$OS_ARCH

PATH=$SROOT/bin:$PATH

I3_DATA=$SROOTBASE/../data
I3_TESTDATA=$SROOTBASE/../data/i3-test-data

PKG_CONFIG_PATH=$SROOT/lib/pkgconfig:$PKG_CONFIG_PATH
LD_LIBRARY_PATH=$SROOT/lib:$LD_LIBRARY_PATH
PYTHONPATH=$SROOT/lib/python2.7/site-packages$PYTHONPATH
PERL5LIB=$SROOT/lib/perl:$SROOT/lib/perl5:$SROOT/lib/perl5/site_perl:$PERL5LIB
MANPATH=$SROOT/man:$SROOT/share/man:$MANPATH
CC=$SROOT/bin/clang
CXX=$SROOT/bin/clang++
ROOTSYS=$SROOT

# MPI, if installed
if [ -d /usr/lib64/openmpi/bin ]; then
	PATH=/usr/lib64/openmpi/bin:$PATH
fi

# GotoBLAS
GOTO_NUM_THREADS=1

VARS="SROOTBASE SROOT I3_DATA I3_TESTDATA PATH MANPATH PKG_CONFIG_PATH LD_LIBRARY_PATH PYTHONPATH ROOTSYS OS_ARCH GCC_VERSION GOTO_NUM_THREADS PERL5LIB GLOBUS_LOCATION CC CXX"

GLOBUS_LOCATION=${SROOT}
# if X509_USER_PROXY is just a filename, qualify it
if [ ! -z "$X509_USER_PROXY" ]; then
	RET=`basename "$X509_USER_PROXY"`
	if [ "$RET" = "$X509_USER_PROXY" ]; then
		X509_USER_PROXY=$PWD/$X509_USER_PROXY
		VARS="${VARS} X509_USER_PROXY"
	fi
fi


# OpenCL
libdirlist=${LD_LIBRARY_PATH}:/usr/lib:/usr/lib64:/lib:/lib64
IFS=:
for p in ${libdirlist}
do
  if [ -e ${p}/libOpenCL.so.1 ]; then
    OpenCL=${p}/libOpenCL.so.1
  fi
  if [ -e ${p}/libgfortran.so.3 ]; then
    GFORTRAN=${p}/libgfortran.so.3
  fi
done
unset IFS
if [ -z ${OPENCL_VENDOR_PATH} ]; then
    if [ -d /etc/OpenCL/vendors ]; then
        OPENCL_VENDOR_PATH=/etc/OpenCL/vendors
    else
        OPENCL_VENDOR_PATH=${SROOTBASE}/../distrib/OpenCL_$OS_ARCH/etc/OpenCL/vendors
    fi
    VARS="${VARS} OPENCL_VENDOR_PATH"
fi
if [ -z ${OpenCL} ]; then
    LD_LIBRARY_PATH=${SROOTBASE}/../distrib/OpenCL_$OS_ARCH/lib/$OS_ARCH:${LD_LIBRARY_PATH}
fi

if [ -z ${GFORTRAN} ]; then
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${SROOT}/tools/gfortran
fi

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


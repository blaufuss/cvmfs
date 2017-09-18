#!/bin/sh

# from bash or tcsh, call this script as:
# eval `/cvmfs/icecube.opensciencegrid.org/setup.sh`

# This is here since readlink -f doesn't work on Darwin
DIR=$(echo "${0%/*}")
SROOTBASE=$(cd "$DIR" && echo "$(pwd -L)")

. $SROOTBASE/os_arch.sh

SROOT=$SROOTBASE/$OS_ARCH

I3_PORTS=$SROOT/i3ports
PATH=$SROOT/bin:$I3_PORTS/bin:$PATH

I3_DATA=$SROOTBASE/../data
I3_TESTDATA=$SROOTBASE/../data/i3-test-data

PKG_CONFIG_PATH=$SROOT/lib/pkgconfig:$PKG_CONFIG_PATH
LD_LIBRARY_PATH=$SROOT/lib:$I3_PORTS/lib:$LD_LIBRARY_PATH
PYTHONPATH=$SROOT/lib/python2.7/site-packages:$I3_PORTS/lib/python2.7/site-packages:$PYTHONPATH
PERL5LIB=$SROOT/lib/perl:$SROOT/lib/perl5:$SROOT/lib/perl5/site_perl:$PERL5LIB
MANPATH=$SROOT/man:$SROOT/share/man:$MANPATH

GCC_VERSION=`gcc -v 2>&1|tail -1|awk '{print $3}'`

# ROOT specific bits
if [ -d $I3_PORTS/root-v5.34.18 ]; then
	: ${ROOTVER="5.34.18"}
elif [ -d $I3_PORTS/root-v5.34.04 ]; then
	: ${ROOTVER="5.34.04"}
elif [ -d $I3_PORTS/root-v5.30.06 ]; then
	: ${ROOTVER="5.30.06"}
elif [ -d $I3_PORTS/root-v5.30.05 ]; then
	: ${ROOTVER="5.30.05"}
fi
: ${ROOTSYS="$I3_PORTS/root-v$ROOTVER"}
PATH=$ROOTSYS/bin:$PATH
LD_LIBRARY_PATH=$ROOTSYS/lib:$LD_LIBRARY_PATH
PYTHONPATH=$ROOTSYS/lib:$PYTHONPATH

# MPI, if installed
if [ -d /usr/lib64/openmpi/bin ]; then
	PATH=/usr/lib64/openmpi/bin:$PATH
fi

# GotoBLAS
GOTO_NUM_THREADS=1

# Java is the future. Enterprise. Continuous Improvement. TPS Reports. Profit.
case $OS_ARCH in
	RHEL_6_x86_64)
		if [ -d /usr/lib/jvm/java-1.6.0-openjdk-1.6.0.33.x86_64 ]; then
			JAVA_HOME=/usr/lib/jvm/java-1.6.0-openjdk-1.6.0.33.x86_64
		elif [ -d /usr/lib/jvm/java-1.6.0-openjdk-1.6.0.0.x86_64 ]; then
			JAVA_HOME=/usr/lib/jvm/java-1.6.0-openjdk-1.6.0.0.x86_64
		else
			JAVA_HOME=/usr/lib/java
		fi ;;
	RHEL_5_i686)
		JAVA_HOME=/usr/java/jdk1.5.0_12   ;;
	RHEL_5_x86_64)
		JAVA_HOME=/usr/java/default       ;;
	RHEL_4_i686)
		JAVA_HOME=/usr/java/j2sdk1.4.2_14 ;;
	RHEL_4_x86_64)
		JAVA_HOME=/usr/java/j2sdk1.4.2    ;;
esac

if ([ -z ${JAVA_HOME} ] || [ ! -f ${JAVA_HOME}/bin/java ]); then
    JAVA_HOME=${SROOTBASE}/../distrib/jdk1.6.0_24_$OS_ARCH
fi
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${JAVA_HOME}/lib:${JAVA_HOME}/jre/lib:${JAVA_HOME}/jre/lib/amd64:${JAVA_HOME}/jre/lib/amd64/server:${JAVA_HOME}/jre/lib/i386:${JAVA_HOME}/jre/lib/i386/server

VARS="SROOTBASE SROOT I3_PORTS I3_DATA I3_TESTDATA PATH MANPATH PKG_CONFIG_PATH LD_LIBRARY_PATH PYTHONPATH ROOTSYS OS_ARCH GCC_VERSION JAVA_HOME GOTO_NUM_THREADS PERL5LIB GLOBUS_LOCATION X509_CERT_DIR"

GLOBUS_LOCATION=${SROOT}
X509_CERT_DIR=${SROOT}/share/certificates
# if X509_USER_PROXY is just a filename, qualify it
if [ ! -z "$X509_USER_PROXY" ]; then
	RET=`basename "$X509_USER_PROXY"`
	if [ "$RET" = "$X509_USER_PROXY" ]; then
		X509_USER_PROXY=$PWD/$X509_USER_PROXY
		VARS="${VARS} X509_USER_PROXY"
	fi
fi

# OpenCL
libdirlist=${LD_LIBRARY_PATH}:/usr/lib:/usr/lib64:/lib:/lib64:/usr/lib/x86_64-linux-gnu
IFS=:
for p in ${libdirlist}
do
  if [ -e ${p}/libOpenCL.so.1 ]; then
    OpenCL=${p}/libOpenCL.so.1
  elif [ -e ${p}/libOpenCL.so ]; then
    OpenCL=${p}/libOpenCL.so
  fi
  if [ -e ${p}/libgfortran.so.3 ]; then
    GFORTRAN=${p}/libgfortran.so.3
  fi
done
unset IFS
CPU_ICD=1
if [ -z ${OPENCL_VENDOR_PATH} ]; then
    if [ -d /etc/OpenCL/vendors ]; then
        OPENCL_VENDOR_PATH=/etc/OpenCL/vendors
        if ( [ ! -e /etc/OpenCL/vendors/amdocl64.icd ] && [ ! -e /etc/OpenCL/vendors/intel64.icd ] ); then
            CPU_ICD=0
        fi
    else
        OPENCL_VENDOR_PATH=${SROOTBASE}/../distrib/OpenCL_${OS_ARCH}/etc/OpenCL/vendors
    fi
    VARS="${VARS} OPENCL_VENDOR_PATH"
fi
if ( [ -z ${OpenCL} ] || [ "$CPU_ICD" = "0" ] ); then
    LD_LIBRARY_PATH=${SROOTBASE}/../distrib/OpenCL_$OS_ARCH/lib/$OS_ARCH:${LD_LIBRARY_PATH}
    if [ "${OPENCL_VENDOR_PATH}" = "/etc/OpenCL/vendors" ]; then
        OPENCL_VENDOR_PATH=`mktemp -d 2>/dev/null || mktemp -d -t 'vendortmp'`
        cp -r /etc/OpenCL/vendors/* ${OPENCL_VENDOR_PATH}
        cp -r ${SROOTBASE}/../distrib/OpenCL_${OS_ARCH}/etc/OpenCL/vendors/* ${OPENCL_VENDOR_PATH}
    fi
fi

if [ -z ${GFORTRAN} ]; then
    LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${SROOT}/tools/gfortran
fi

CUR_SHELL=`readlink "/proc/$$/exe"|awk -F'/' '{print $NF}'`

for name in ${VARS}
do
  eval VALUE=\$$name
  case ${CUR_SHELL} in 
	tcsh)
		echo 'setenv '$name' '\"$VALUE\"' ;' ;;
	csh)
		echo 'setenv '$name' '\"$VALUE\"' ;' ;;
	*)
		echo 'export '$name=\"$VALUE\"' ;' ;;
  esac
done


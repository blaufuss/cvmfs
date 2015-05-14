#!/bin/sh

# Usage: bootstrap_platform_tools.sh scratchdir

# check that we're in the env
if [ -z $SROOT ]; then
	echo Must be in environment with SROOT set.
	exit 1
fi

# Versions and tools
PYVER=2.7.8
PYDISTRIBUTEVER=0.6.49
PIPVER=1.4.1
GNUPLOTVER=4.6.3
TCLVER=8.5.14
HDF5VER=1.8.11
QTVER=4.8.5
FFTWVER=3.3.4
HEALPIXVER=3.11
BOOSTNUMPYVER=0.2.2
ZMQVER=4.0.4
SQLITEVER=3080600
#GLOBUSVER=5.2.5
GSOAPVER=2.8.21
VOMSVER=2.0.12-2
PORTS_TO_INSTALL="boost_1.38.0 gsl_1.8 gsl_1.14 gsl_1.16 GotoBLAS2+bulldozer libxml2_2.7.8 slalib-c_0.0 cdk sprng_2.0a Minuit2_5.24.00 cfitsio_3.27 SuiteSparse photonics_1.67 photonics_1.73 log4cplus_1.0.2 log4cplus_1.0.4 rdmc_2.9.5 anis_1.8.2 mysql_4.1.20 healpix"
PYTHON_PKGS_TO_INSTALL="numpy==1.7.1 scipy==0.12.0 readline==6.2.4.1 ipython==2.4.0 pyfits==3.1.2 numexpr==2.2.1 Cython==0.19.1 tables==3.0.0 gnuplot-py==1.8 matplotlib==1.3.0 Sphinx==1.1.3 healpy==1.7.3 pyMinuit2==1.1.0 spectrum==0.5.6 urwid==1.1.1 PyMySQL==0.6.1 pyFFTW==0.9.2"

if [ ! $OS_ARCH = "Ubuntu_14_x86_64" ]; then
	PORTS_TO_INSTALL="$PORTS_TO_INSTALL root_5.28.00d+nox11 root_5.34.18+nox11"
fi

# Platform-dependent parts
if [ $(uname -s) = Linux ]; then
	PORTS_TO_INSTALL="$PORTS_TO_INSTALL libarchive geant4_4.9.5 pythia_root_6.4.16 root_5.30.06+mathmore+nox11 genie_2.6.4"
fi

# Extra things for grid tools
#GLOBUSVER=5.2.4
if [ $OS_ARCH = "RHEL_5_x86_64" ]; then
	PYTHON_PKGS_TO_INSTALL="$PYTHON_PKGS_TO_INSTALL pyOpenSSL==0.12"
else
	PYTHON_PKGS_TO_INSTALL="$PYTHON_PKGS_TO_INSTALL pyOpenSSL==0.13"
fi
PYTHON_PKGS_TO_INSTALL="$PYTHON_PKGS_TO_INSTALL pyasn1==0.1.7 coverage==3.7.1 flexmock==0.9.7" # apsw pycurl

# Extra things for ipython notebok
PYTHON_PKGS_TO_INSTALL="$PYTHON_PKGS_TO_INSTALL pyzmq==14.3.1 tornado==4.0.2"

# ----------------- Installation---------------------

# Figure out how to download things
if curl -Ls -o /dev/null http://www.google.com; then
	FETCH="curl -LO"
elif wget -q -O /dev/null http://www.google.com; then
	FETCH="wget"
elif fetch -o /dev/null http://www.google.com; then
	FETCH="fetch"
else
	echo "Cannot figure out how to download things!"
	exit 1
fi

set -e 
trap "echo Build Error" EXIT

mkdir -p $SROOT
mkdir -p $1

# TCL/TK
if [ ! -f $SROOT/bin/tclsh ]; then
	cd $1
	$FETCH http://iweb.dl.sourceforge.net/project/tcl/Tcl/$TCLVER/tcl$TCLVER-src.tar.gz
	$FETCH http://iweb.dl.sourceforge.net/project/tcl/Tcl/$TCLVER/tk$TCLVER-src.tar.gz
	tar xvzf tcl$TCLVER-src.tar.gz
	tar xvzf tk$TCLVER-src.tar.gz
	cd tcl$TCLVER/unix
	./configure --prefix=$SROOT --disable-shared
	make
	make install install-libraries
	cd $1
	cd tk$TCLVER/unix
	# TK is an optional dependency
	(./configure --prefix=$SROOT && make && make install) || true
	ln -s $SROOT/bin/tclsh8.5 $SROOT/bin/tclsh
fi

# SQLite
if [ ! -f $SROOT/lib/libsqlite3.so ]; then
	cd $1
	$FETCH http://www.sqlite.org/2014/sqlite-autoconf-$SQLITEVER.tar.gz
	tar xvzf sqlite-autoconf-$SQLITEVER.tar.gz
	cd sqlite-autoconf-$SQLITEVER
	./configure --prefix=$SROOT
	make
	make install
fi

# Python
if [ ! -f $SROOT/bin/python ]; then
	cd $1
	$FETCH http://www.python.org/ftp/python/$PYVER/Python-$PYVER.tgz
	tar xvzf Python-$PYVER.tgz
	cd Python-$PYVER
	./configure --prefix=$SROOT --enable-shared
	make
	make install
	if python -c 'import sqlite3'; then
		true
	else
		echo python is missing sqlite3
		exit 1
	fi
fi

# Python Distribute
if python -c 'import setuptools'; then
	true
else
	cd $1
	$FETCH http://pypi.python.org/packages/source/d/distribute/distribute-$PYDISTRIBUTEVER.tar.gz
	tar xvzf distribute-$PYDISTRIBUTEVER.tar.gz
	cd distribute-$PYDISTRIBUTEVER
	python setup.py build
	python setup.py install --prefix=$SROOT
fi

# Pip
if [ ! -f $SROOT/bin/pip ]; then
	cd $1
	$FETCH http://pypi.python.org/packages/source/p/pip/pip-$PIPVER.tar.gz
	tar xvzf pip-$PIPVER.tar.gz
	cd pip-$PIPVER
	python setup.py build
	python setup.py install --prefix=$SROOT
fi

# I3_PORTS
if [ ! -f $I3_PORTS/bin/port ]; then
	cd $1
	svn co http://code.icecube.wisc.edu/icetray-dist/tools/DarwinPorts/trunk port_source
	cd port_source
	./configure --prefix=$I3_PORTS --with-python=$SROOT/bin/python --with-tcl=$SROOT/lib --with-tclinclude=$SROOT/include --with-install-group=`groups | cut -f 1 -d ' '`
	make
	make install
fi

set +e
unset ROOTSYS
eval `$SROOTBASE/setup.sh`
python -c "import os,sys;sys.exit(os.path.exists('/etc/os-release') and any([1 for line in open('/etc/os-release') if 'ubuntu' in line]))"
IS_UBUNTU=$?
set -e

if [ $IS_UBUNTU = 1 ]; then
	echo "This is Ubuntu. Attempting to build Qt4 manually."
	# QT 4.8 manual installation on Ubuntu
	if [ ! -f $SROOT/bin/qmake ]; then
		cd $1
		$FETCH http://download.qt-project.org/archive/qt/4.8/$QTVER/qt-everywhere-opensource-src-$QTVER.tar.gz
		tar xvzf qt-everywhere-opensource-src-$QTVER.tar.gz
		cd qt-everywhere-opensource-src-$QTVER
		sed -i 's/OPT_CONFIRM_LICENSE=no/OPT_CONFIRM_LICENSE=yes/g' configure
		./configure --prefix=$SROOT -opensource -no-accessibility -no-sql-db2 \
				-no-sql-ibase -no-sql-mysql -no-sql-oci -no-sql-odbc \
				-no-sql-psql -no-sql-sqlite -no-sql-sqlite2 \
				-no-sql-sqlite_symbian -no-sql-tds \
				-no-xmlpatterns -no-multimedia -no-phonon -no-phonon-backend \
				-no-webkit -no-javascript-jit -no-script -no-scripttools \
				-no-declarative -no-nis -nomake examples -nomake demos \
				-nomake docs -nomake translations -fast -silent
		make
		make install
	fi
else
	echo "This is not Ubuntu. Building Qt4 as part of I3_PORTS"
	PORTS_TO_INSTALL="$PORTS_TO_INSTALL qt_4.6.4 qt_4.8.6"
fi

port -v sync
port -v upgrade outdated
for port in $PORTS_TO_INSTALL; do
	port=`echo $port | sed 's/\+/ \+/g'`
	#port -v upgrade $port
	port -v install $port
done

# Hack for old software
rm -f $I3_PORTS/root-v5.24.00b
ln -s root-v5.28.00d $I3_PORTS/root-v5.24.00b

set +e
unset ROOTSYS
eval `$SROOTBASE/setup.sh`
set -e

# Gnuplot
if [ ! -f $SROOT/bin/gnuplot ]; then
	cd $1
	$FETCH http://iweb.dl.sourceforge.net/project/gnuplot/gnuplot/$GNUPLOTVER/gnuplot-$GNUPLOTVER.tar.gz
	tar xvzf gnuplot-$GNUPLOTVER.tar.gz
	cd gnuplot-$GNUPLOTVER
	./configure --prefix=$SROOT --without-linux-vga --without-lisp-files --without-tutorial --with-bitmap-terminals
	make
	# Fix brokenness build system with hard dependencies on optional files
	touch docs/gnuplot-eldoc.el docs/gnuplot-eldoc.elc
	make install
fi

# HDF5
if [ ! -f $SROOT/bin/h5ls ]; then
	cd $1
	$FETCH http://www.hdfgroup.org/ftp/HDF5/releases/hdf5-$HDF5VER/src/hdf5-$HDF5VER.tar.bz2
	tar xvjf hdf5-$HDF5VER.tar.bz2
	cd hdf5-$HDF5VER
	./configure --prefix=$SROOT --disable-debug --enable-cxx --enable-production --enable-strict-format-checks --with-zlib=/usr
	make
	make install
fi

# ZMQ
if [ ! -f $SROOT/lib/libzmq.so ]; then
	cd $1
	$FETCH http://download.zeromq.org/zeromq-$ZMQVER.tar.gz
	tar xvzf zeromq-$ZMQVER.tar.gz
	cd zeromq-$ZMQVER
	./configure --prefix=$SROOT
	make
	make install
fi

# Dependencies for python stuff
export BLAS=$I3_PORTS/lib/libgoto2.so
export LAPACK=$I3_PORTS/lib/libgoto2.so
export HDF5_DIR=$SROOT
export CFITSIO_EXT_PREFIX=$I3_PORTS
#export LDFLAGS="-L$SROOT/lib"

# FFTW
if [ ! -f $SROOT/lib/libfftw3l.so ]; then
	cd $1
	$FETCH http://www.fftw.org/fftw-$FFTWVER.tar.gz
	tar xvzf fftw-$FFTWVER.tar.gz
	cd fftw-$FFTWVER
	CC="cc -mtune=generic" ./configure --prefix=$SROOT --enable-shared --enable-float --enable-threads
	make
	make install

	cd $1
	rm -rf fftw-$FFTWVER
	tar xvzf fftw-$FFTWVER.tar.gz
	cd fftw-$FFTWVER
	CC="cc -mtune=generic" ./configure --prefix=$SROOT --enable-shared --enable-long-double --enable-threads
	make
	make install

	cd $1
	rm -rf fftw-$FFTWVER
	tar xvzf fftw-$FFTWVER.tar.gz
	cd fftw-$FFTWVER
	CC="cc -mtune=generic" ./configure --prefix=$SROOT --enable-shared --enable-threads
	make
	make install
fi

# C Healpix
if [ ! -f $SROOT/lib/libchealpix.so ]; then
	cd $1
	$FETCH http://iweb.dl.sourceforge.net/project/healpix/Healpix_$HEALPIXVER/Healpix_3.11_2013Apr24.tar.gz
	tar xvzf Healpix_3.11_2013Apr24.tar.gz
	cd Healpix_$HEALPIXVER/src/C/subs
	make shared CFITSIO_INCDIR=$I3_PORTS/include CFITSIO_LIBDIR=$I3_PORTS/lib
	make install INCDIR=$SROOT/include LIBDIR=$SROOT/lib
fi

# Python packages
for pkg in $PYTHON_PKGS_TO_INSTALL; do
	case $pkg in
	pyFFTW*)
		CFLAGS="-I $SROOT/include"  pip install -b $1 pyFFTW
		;;
	*)
		pip install -b $1 $pkg
		;;
	esac
done

# Boost Numpy
if [ ! -f $SROOT/lib/libboost_numpy.so ]; then
	cd $1
	$FETCH https://github.com/martwo/BoostNumpy/archive/V$BOOSTNUMPYVER.tar.gz
	tar xvzf V$BOOSTNUMPYVER.tar.gz
	cd BoostNumpy-$BOOSTNUMPYVER
	rm -rf build
	mkdir -p build
	cd build
	cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$SROOT -DBOOST_INCLUDEDIR=$SROOT/i3ports/include/boost-1.38.0 -DBOOST_LIBRARYDIR=$SROOT/i3ports/lib/boost-1.38.0 ..
	make
	make install
fi

# Globus
if [ ! -f $SROOT/bin/globus-url-copy -a ! -z "$GLOBUSVER" ]; then
	cd $1
	$FETCH http://www.globus.org/ftppub/gt5/`echo $GLOBUSVER | cut -f 1,2 -d .`/$GLOBUSVER/installers/src/gt$GLOBUSVER-all-source-installer.tar.gz
	tar xvzf gt$GLOBUSVER-all-source-installer.tar.gz
	cd gt$GLOBUSVER-all-source-installer
	./configure --prefix=$SROOT
	make gpt globus-data-management-client
	make install
fi

# GSOAP - a requirement for VOMs
if [ ! -f $SROOT/bin/wsdl2h ]; then
	cd $1
	$FETCH http://iweb.dl.sourceforge.net/project/gsoap2/gSOAP/gsoap_$GSOAPVER.zip
	unzip -o gsoap_$GSOAPVER.zip
	cd gsoap-`echo $GSOAPVER | cut -f 1,2 -d .`
	./configure --prefix=$SROOT
	make
	make install
fi

# VOMs
if [ ! -f $SROOT/bin/voms-proxy-init -a ! -z "$VOMSVER" ]; then
	cd $1
	$FETCH https://github.com/italiangrid/voms/archive/v$VOMSVER.tar.gz
	tar xvzf v$VOMSVER.tar.gz
	cd voms-$VOMSVER
	./autogen.sh
	./configure --prefix=$SROOT --without-interfaces --without-server --disable-shared --with-gsoap-wsdl2h=$SROOT/bin/wsdl2h
	make
	make install
fi

set +e
rm -rf $1
trap true EXIT
echo Build and installation successful


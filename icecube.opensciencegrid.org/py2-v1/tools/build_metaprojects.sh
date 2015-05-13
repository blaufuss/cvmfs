#!/bin/sh

METABASE=$SROOTBASE/metaprojects
cd $METABASE

successes=""
failures=""
cores=1
#cores=$(grep processor /proc/cpuinfo|wc -l)

skip_list=""
if ( [ $OS_ARCH = "Ubuntu_12_x86_64" ] || [ $OS_ARCH = "Ubuntu_14_x86_64" ] ); then
	skip_list="std-processing/11-02-02 std-processing/11-02-02-future-compat icerec/V04-00-01"
	if [ $OS_ARCH = "Ubuntu_14_x86_64" ]; then
		skip_list="${skip_list} icerec/V04-01-00"
	fi
fi

for metaproject in */*; do
	skip="0"
	for m2 in $skip_list; do
		if [ "$m2" = "$metaproject" ]; then
			skip="1";
			break;
		fi
	done
	if [ "$skip" = "1" ]; then
		echo Skipping $metaproject
		continue;
	fi
	echo Starting build of $metaproject...
	if [ ! -f $SROOT/metaprojects/$metaproject/Makefile ]; then
		rm -rf $SROOT/metaprojects/$metaproject
		mkdir -p $SROOT/metaprojects/$metaproject
	else
		# Avoid stale entries when rebuilding
		rm -f $SROOT/metaprojects/$metaproject/CMakeCache.txt
	fi
	cd $SROOT/metaprojects/$metaproject
	if [ $OS_ARCH = "RHEL_5_x86_64" ]; then
		CC=gcc44 CXX=g++44 cmake -DCMAKE_BUILD_TYPE=Release -DCOPY_PYTHON_DIR=True $METABASE/$metaproject;
		CC=gcc44 CXX=g++44 cmake -DCMAKE_BUILD_TYPE=Release -DCOPY_PYTHON_DIR=True $METABASE/$metaproject;
	else
		cmake -DCMAKE_BUILD_TYPE=Release -DCOPY_PYTHON_DIR=True $METABASE/$metaproject;
		cmake -DCMAKE_BUILD_TYPE=Release -DCOPY_PYTHON_DIR=True $METABASE/$metaproject;
	fi
	make -j$cores
	if [ $? = 0 ]; then
		successes="$successes
	$metaproject";
	else
		failures="$failures
	$metaproject";
	fi
	python -m compileall -fq lib/icecube
done

echo Metaproject build report
echo Successful builds:
echo "$successes"
echo Failed builds:
echo "$failures"


#!/bin/sh

# .bash_profile

if [ -x /usr/bin/lsb_release ]; then
	DISTRIB=`lsb_release -si`
	VERSION=`lsb_release -sr`
	CPU=`uname -m`
else
	DISTRIB=`uname -s`
	VERSION=`uname -r`
	CPU=`uname -m`
fi

# Map binary compatible operating systems and versions onto one another
case $DISTRIB in
	"RedHatEnterpriseClient" | "RedHatEnterpriseServer" | "ScientificSL" | "Scientific" | "CentOS" | "ScientificFermi")
		DISTRIB="RHEL"
		VERSION=`lsb_release -sr | cut -d '.' -f 1`
		;;
	"Ubuntu")
		VERSION=`lsb_release -sr | cut -d '.' -f 1`
		;;
	"Debian")
		DISTRIB="Ubuntu"
		if echo $VERSION | grep -q '8\.\?'; then
			VERSION=14
		elif echo $VERSION | grep -q '7\.\?'; then
			VERSION=11
		elif echo $VERSION | grep -q '6\.\?'; then
			VERSION=10
		fi
		;;
	"FreeBSD")
		VERSION=`uname -r | cut -d '.' -f 1`
		CPU=`uname -p`
		;;
	"Darwin")
		VERSION=`uname -r | cut -d '.' -f 1`
		;;
	"Linux")
		# Damn. Try harder with the heuristics.
		if echo $VERSION | grep -q '\.el6\.\?'; then
			DISTRIB="RHEL"
			VERSION=6
		elif echo $VERSION | grep -q '\.el5\.\?'; then
			DISTRIB="RHEL"
			VERSION=5
		fi
esac

OS_ARCH=${DISTRIB}_${VERSION}_${CPU}
GCC_VERSION=`gcc -v 2>&1|tail -1|awk '{print $3}'`

export OS_ARCH
export GCC_VERSION
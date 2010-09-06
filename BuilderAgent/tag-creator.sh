#!/bin/bash

visit() {
    local FILE=$1;
    local PROJ=${FILE%\.*} # gets only what comes before the last '.'

    if [[ $PKG_LIST =~ "^$PROJ | $PROJ$| $PROJ |^$PROJ$" ]]; then
        # This is one of the developer's project files. Get from his tag
	cvs up -r $PTAG CMSDIST/$FILE
    elif [ -f $WEB/$PROJ.$REPO ]; then
	# If it is another top-level project, get from latest release
	local RELTAG=$(cat $WEB/$PROJ.$REPO|cut -d"|" -f6 | tr -d " \t")
	cvs up -r $RELTAG CMSDIST/$FILE
    elif [ -f CMSDIST.base/$FILE ]; then
	# Tries to get from latest base release
	cvs up -r $BTAG CMSDIST/$FILE
    elif [ "$PTAG" != "HEAD" ]; then
	# Since not possible by other means, get from developer's tag 
	cvs up -r $PTAG CMSDIST/$FILE
    fi
}

search() {
    local PROJ=$1;
    [ -f CMSDIST/${PROJ}.spec ] && return # skip already visited files

    visit ${PROJ}.spec
    for PATCH in $(grep "Patch" CMSDIST/${PROJ}.spec|grep -v "#"|cut -d" " -f2-); do
	visit ${PATCH}.patch
    done
    for DEP in $(grep "Requires: " CMSDIST/${PROJ}.spec|grep -v "#"|cut -d" " -f2-); do
	search $DEP
    done
}

#
# Main
#
[ $# -lt 2 ] && echo "Usage: $0 <proj-cmsdist-tag> <project> [<other-pkgs> ...]" && exit 1
[ -d "./CMSDIST" ] && echo "CMSDIST dir already exist" && exit 1
[ -d "./CMSDIST.base" ] && echo "CMSDIST.base dir already exist" && exit 2

PTAG=$1; shift;
PROJ=$1; shift;
PKG_LIST="$PROJ $@"

CFGFILE="/build/diego/builder/sw/config"
source $CFGFILE
REPO="comp"
BTAG=$(cat $WEB/base.$REPO|cut -d"|" -f6 | tr -d " \t")

cvs co -d CMSDIST.base -r $BTAG CMSDIST
cvs co -r $BTAG CMSDIST/cmsos.file CMSDIST/rpm-preamble.file CMSDIST/gcc.spec CMSDIST/binutils-2.19.1-fix-gold.patch

search $PROJ

# Exceptions: specs that require other files
if [ -f CMSDIST/sqlite.spec ]; then
	visit sqlite_`head -n1 CMSDIST/sqlite.spec | cut -d" " -f5`_readline_for_32bit_on_64bit_build.patch
fi

if [ -f CMSDIST/oracle.spec ]; then
        visit oracle-license.file
fi

if [ -f CMSDIST/libjpg.spec ]; then
	visit config.sub-amd64.file
fi

if [ -f CMSDIST/mysql-deployment.spec ]; then
	visit mysql-deployment.sh.file
fi

exit 0
#
# end of script
#


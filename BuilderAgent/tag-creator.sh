#!/bin/bash

visit() {
    local FILE=$1;
    local PROJ=${FILE%\.*} # gets only what comes before the last '.'

    if [[ $PKG_LIST =~ "^$PROJ | $PROJ$| $PROJ |^$PROJ$" ]]; then
        # This is one of the developer's project files. Get from his tag
	cvs -Q up -r $PTAG CMSDIST/$FILE
    elif [ -f $WEB/$PROJ.$REPO ]; then
	# If it is another top-level project, get from latest release
	local RELTAG=$(cat $WEB/$PROJ.$REPO|cut -d"|" -f6 | tr -d " \t")
	cvs -Q up -r $RELTAG CMSDIST/$FILE
    elif [ -f CMSDIST.base/$FILE ]; then
	# Tries to get from the base release
	cvs -Q up -r $BTAG CMSDIST/$FILE
    elif [ "$PTAG" != "HEAD" ]; then
	# Since not possible by other means, get from developer's tag 
	cvs -Q up -r $PTAG CMSDIST/$FILE
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
[ $# -lt 3 ] && echo "Usage: $0 <base-tag> <proj-cmsdist-tag> <project> [<other-pkgs> ...]" && exit 1
[ -d "./CMSDIST" ] && echo "CMSDIST dir already exists" && exit 1
[ -d "./CMSDIST.base" ] && echo "CMSDIST.base dir already exists" && exit 2

BTAG=$1; PTAG=$2; PROJ=$3; shift 3;
PKG_LIST="$PROJ $@"

CFGFILE="/build/diego/builder/sw/config"
source $CFGFILE
REPO="comp"

cvs -Q co -d CMSDIST.base -r $BTAG CMSDIST ||
    { echo "Could not fetch base tag $BTAG."; exit 3; }
cvs -Q co -r $BTAG CMSDIST/cmsos.file CMSDIST/rpm-preamble.file CMSDIST/gcc.spec CMSDIST/binutils-2.19.1-fix-gold.patch

search $PROJ

# Exceptions: specs that require other files
[ -f CMSDIST/sqlite.spec ] &&
    visit sqlite_`head -n1 CMSDIST/sqlite.spec | cut -d" " -f5`_readline_for_32bit_on_64bit_build.patch

[ -f CMSDIST/oracle.spec ] &&
    visit oracle-license.file

[ -f CMSDIST/libjpg.spec ] &&
    visit config.sub-amd64.file

[ -f CMSDIST/mysql-deployment.spec ] &&
    visit mysql-deployment.sh.file

[ -f CMSDIST/couchdb.spec ] &&
    visit couch_cms_auth.erl.file

exit 0

# end of script



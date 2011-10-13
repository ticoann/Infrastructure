#!/bin/bash

CFGFILE=$1; shift
[ -n "$CFGFILE" ] || { echo "$0: usage $0 <cfgfile>"; exit 1; }
[ -f "$CFGFILE" ] || { echo "$0: could not find config file $CFGFILE"; exit 2; }
source $CFGFILE

[ -n "$*" ]  && AGE=$(date --date="$*" +%s 2> /dev/null)
[ -z "$AGE" ] && AGE=$(date --date="3 months ago" +%s)
LASTCLEAN=$(cat $WEB/last_tag_clean 2> /dev/null || echo 0)

LAST=$(egrep -h -o "bld_.*\>" $WEB/*comp $WEB/*comp.pre|sort -u)
HIST=$(egrep -h -o "bld_.*\>" $WEB/*history | sort -u | \
       egrep -v "${LAST// /|}")
for TAG in $HIST; do
    TAGAGE=$(echo $TAG | cut -d"_" -f2)
    if [ $TAGAGE -lt $AGE -a $TAGAGE -ge $LASTCLEAN ]; then
	cvs -Q rtag -d $TAG CMSDIST &> /dev/null || exit 1
    fi
done

echo $AGE > $WEB/last_tag_clean

#!/bin/bash

CFGFILE="/build/dmwmbld/sw/current/config"
source $CFGFILE

[ -n "$*" ]  && AGE=$(date --date="$*" +%s 2> /dev/null)
[ -z "$AGE" ] && AGE=$(date --date="3 months ago" +%s)
LASTCLEAN=$(cat $WEB/last_tag_clean 2> /dev/null || echo 0)

LAST=$(egrep -h -o "builder_20.*\>" $WEB/*comp $WEB/*comp.pre|sort -u)
HIST=$(egrep -h -o "builder_20.*\>" $WEB/*history | sort -u | \
       egrep -v "${LAST// /|}")
for TAG in $HIST; do
    DATE=${TAG#*_}; DATE=${DATE%%_*}
    TIME=${TAG%_*}; TIME=${TIME##*_}
    TAGAGE=$(date --date="$DATE ${TIME//-/:}" +%s)
    if [ $TAGAGE -lt $AGE -a $TAGAGE -ge $LASTCLEAN ]; then
	cvs -Q rtag -d $TAG CMSDIST &> /dev/null || exit 1
    fi
done

echo $AGE > $WEB/last_tag_clean

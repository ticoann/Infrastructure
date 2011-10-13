#!/bin/bash

CFGFILE=$1; shift
[ -n "$CFGFILE" ] || { echo "$0: usage $0 <cfgfile>"; exit 1; }
[ -f "$CFGFILE" ] || { echo "$0: could not find config file $CFGFILE"; exit 2; }
source $CFGFILE
source $BUILDFUNCS
LOG_FILES="$BUILDER_ROOT/logs/*-*-*_*-*-*"

[ -n "$*" ]  && AGE=$(date --date="$*" +%s 2> /dev/null)
[ -z "$AGE" ] && AGE=$(date --date="1 week ago" +%s)
for FILE in $LOG_FILES; do
    LAST_CHANGE=$(stat $statfmt $FILE 2> /dev/null || date +%s)
    [ $LAST_CHANGE -lt $AGE ] && rm "$FILE"  &> /dev/null
done

exit 0

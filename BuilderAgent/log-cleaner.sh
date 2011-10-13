#!/bin/bash

CFGFILE="/build/dmwmbld/sw/current/config"
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

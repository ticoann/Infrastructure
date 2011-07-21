#! /bin/bash
#
# Squash all patches in a series together - use wisely, it assumes that
# everything in the series should be squashed - delete/hide patches you don't
# want squashed together.
#

stg pop -n `stg series|wc -l` >> /dev/null
for (( COUNTER=1; COUNTER<=`stg series|wc -l`; COUNTER+=1 )); do
    stg push >> /dev/null
    stg edit --save-template - >> squash.tmp
    echo >> squash.tmp
done

stg squash --file squash.tmp -n squashed-patch-series `stg series| awk {'printf "%s ", $2'}`

rm squash.tmp
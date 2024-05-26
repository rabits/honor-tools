#!/bin/sh

# Script tries to find all update files on update.hihonorcdn.com (filelist.xml & changelog.xml) and
# stores those files into update_hihonorcdn_com_all_* directory for further processing

from=000000
to=400000

d="update_hihonorcdn_com_all_$from-$to"

worker() {
    start=$1
    end=$2
    d2="$d/${start}_${end}"
    echo "Running worker ${start}_${end}";
    mkdir -p "$d2"
    for i in `seq $end -1 $start`; do
        echo "Getting v${i}";
        path="$d2/v${i}_filelist.xml"
        curl -so "${path}" http://update.hihonorcdn.com/TDS/data/bl/files/v$i/f1/full/filelist.xml
        if ! (grep '<packageType>' "${path}"); then
            rm -f "${path}"
        fi
        path="$d2/v${i}_changelog.xml"
        curl -so "${path}" http://update.hihonorcdn.com/TDS/data/bl/files/v$i/f1/changelog.xml
        if ! (grep '<language' "${path}"); then
            rm -f "${path}"
        fi
    done
}

prev=''
for thread in `seq $from 20000 $to`; do
    if [ "x$prev" != 'x' ]; then
        worker $(($prev+1)) $thread &
    fi
    prev=$thread
done

wait

echo "Done"

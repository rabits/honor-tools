#!/bin/sh

# Script goes into subdirs of the provided directory and looks for *_filelist.xml files to download
# zip files tails in parallel to get VERSION.mbn which contains the actual version of the update
#
# Usage:
# $ ./get_version_mbn.sh update_hihonorcdn_com_all_000000-400000

SEARCH_DIR="$1"
[ "x$SEARCH_DIR" != 'x' ] || exit 1

worker() {
    path="$1"
    echo "Running worker in $path";
    for xml in `find "$path" -mindepth 1 -maxdepth 1 -name '*_filelist.xml'`; do
        [ ! -f "${xml}.version_mbn" ] || continue
        echo "Looking at ${xml}";
        fname=$(grep -o 'spath>[^<]\+' "${xml}" | cut -d'>' -f 2)
        if [ "x$fname" = 'x' ]; then
            # The filelist is not about base
            continue
        fi
        version=$(basename "$xml" | cut -d_ -f1)
        echo "Looking into http://update.hihonorcdn.com/TDS/data/bl/files/$version/f1/full/$fname"
        mbn_version=$(./update_zip_version_mbn.py "http://update.hihonorcdn.com/TDS/data/bl/files/$version/f1/full/$fname")
        echo "Found version: $mbn_version"
        if [ "x$mbn_version" != 'x' ]; then
            echo "$mbn_version" > "${xml}.version_mbn"
        fi
    done
}

prev=''
for path in "$SEARCH_DIR"/*; do
    worker "$path" &
done

wait

echo "Done"

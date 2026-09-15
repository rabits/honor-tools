#!/bin/sh
# Honor Magic V2 - VER-N49

SEARCH_DIR="$1"
if [ "x$SEARCH_DIR" = 'x' ]; then
    echo 'Please specify directory to search in'
    exit 1
fi

grep -r 'VER-LGRP2-OVS' "$SEARCH_DIR" | grep 'version_mbn' | sed 's/\(.*\):\(.*\)/\2        \1/' | sort

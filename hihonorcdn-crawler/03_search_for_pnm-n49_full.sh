#!/bin/sh
# Honor Magic V6 - PNM-N49

SEARCH_DIR="$1"
if [ "x$SEARCH_DIR" = 'x' ]; then
    echo 'Please specify directory to search in'
    exit 1
fi

grep -r 'PNM-LGRP2-OVS' "$SEARCH_DIR" | grep 'version_mbn' | sed 's/\(.*\):\(.*\)/\2        \1/' | sort

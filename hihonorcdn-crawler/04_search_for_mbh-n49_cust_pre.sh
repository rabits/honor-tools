#!/bin/sh

SEARCH_DIR="$1"
[ "x$SEARCH_DIR" != 'x' ] || exit 1

grep -r 'MBH-N49-' "$SEARCH_DIR" | grep 'version_mbn' | sed 's/\(.*\):\(.*\)/\2        \1/' | sort

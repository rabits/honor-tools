#!/usr/bin/env python3

# Finds VERSION.mbn in the remote update zip file and shows its content
# It downloads just a tail of the zip file to skip the full zip downloading

import sys, os.path
import urllib.request
from tempfile import TemporaryFile
from zipfile import ZipFile

if len(sys.argv) < 2 or not sys.argv[1].startswith('http'):
    print('ERROR: Please provide http(s) url as argument')
    sys.exit(1)

# Downloading last 20KB with zip records
hdr = {'Range': 'bytes=-20480'}
req = urllib.request.Request(sys.argv[1], headers=hdr)
res = urllib.request.urlopen(req)

with TemporaryFile('w+b') as fh:
    fh.write(res.read())
    zf = ZipFile(fh)
    zinfo = zf.getinfo('VERSION.mbn')
    if zinfo.header_offset < 0:
        # The VERSION.mbn is located in the middle of the file,
        # so downloading it and rewriting the beginning of the temp file
        fsize = int(res.getheader('Content-Range').split('-')[0].split(' ')[-1])
        # We need to get just ~256 bytes, because the VERSION.mbn is not that huge
        hdr2 = {'Range': 'bytes={}-{}'.format(fsize+zinfo.header_offset, fsize+zinfo.header_offset+256)}
        req2 = urllib.request.Request(sys.argv[1], headers=hdr2)
        res2 = urllib.request.urlopen(req2)
        fh.seek(0)
        fh.write(res2.read())
        fh.seek(0)
        zinfo.header_offset = 0
    print(zf.read(zinfo).decode('UTF-8').strip())

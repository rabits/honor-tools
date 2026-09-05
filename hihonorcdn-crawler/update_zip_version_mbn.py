#!/usr/bin/env python3

# Finds VERSION.mbn in the remote update zip file and shows its content
# It downloads just a tail of the zip file to skip the full zip downloading

import io
import sys
import time
import requests
from zipfile import ZipFile

class HttpRangeFile:
    def __init__(self, url, session=None):
        self.url = url
        self.session = session or requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/145.0'})
        self.pos = 0
        #r = self.session.head(url, allow_redirects=True, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/145.0'})
        with self.session.get(url, allow_redirects=True, stream=True) as r:
            r.raise_for_status()
            if r.headers.get("Accept-Ranges", "").lower() != "bytes":
                raise RuntimeError("Server does not support 'range' header")
            self.size = int(r.headers["Content-Length"])

    def seek(self, offset, whence=0):
        if whence == 0:
            self.pos = offset
        elif whence == 1:
            self.pos += offset
        elif whence == 2:
            self.pos = self.size + offset
        return self.pos

    def tell(self):
        return self.pos

    def read(self, size=-1):
        if size < 0:
            end = self.size - 1
        else:
            end = min(self.pos + size - 1, self.size - 1)
        if self.pos > end:
            return b""
        headers = {"Range": f"bytes={self.pos}-{end}"}
        with self.session.get(self.url, headers=headers, stream=True) as r:
            r.raise_for_status()
            if r.status_code not in (200, 206):
                raise RuntimeError(f"Expected 206, got: {r.status_code}")
            data = r.content
            self.pos += len(data)
            return data

    def seekable(self):
        return True

url = sys.argv[1]

for i in [0, 1]:
    try:
        with ZipFile(HttpRangeFile(url)) as zf:
            #print(zf.namelist())
            with zf.open("VERSION.mbn") as f:
                print(f.read().decode('UTF-8').strip())
                break
    except Exception as e:
        if "There is no item named 'VERSION.mbn' in the archive" in f"{e}":
            continue
        print(f"Retry {url}: {e}", file=sys.stderr)

        import logging

        # These two lines enable debugging at httplib level (requests->urllib3->http.client)
        # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
        # The only thing missing will be the response.body which is not logged.
        try:
            import http.client as http_client
        except ImportError:
            # Python 2
            import httplib as http_client
        http_client.HTTPConnection.debuglevel = 1

        # You must initialize logging, otherwise you'll not see debug output.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

        time.sleep(5)

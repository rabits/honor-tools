# Honor Tools

A collection of tools for exploring Honor devices (particularly VER-N49 - Honor Magic V2), but could
be useful for anyone who have honor device.

XDA-Developers forum: https://xdaforums.com/t/unlock-bootloader-code-for-honor-magic-v2-root-with-magisk.4663415/post-89499716

## HonorSuite patcher

Scripts to override HonorSuite binaries to allow mitmproxy to intercept the requests and see what
kind of url's & parameters it's using. You will also need [MITMProxy](https://mitmproxy.org/) and
[Proxifier](https://www.proxifier.com/) to properly redirect the HonorSuite requests.

How to setup interceptor: https://xdaforums.com/t/op11-edl-downloadtool-to-restore-your-device-to-oxygenos-coloros.4607995/

Also please check the scripts headers in the directory to get a clue how to use them. The produced
patched files are not replacing HonorSuite files to make it happy with checksums.

## Crawler for update.hihonorcdn.com

Allows to get all the xml files from update.hihonorcdn.com and find versions of update zip files to
simplify your search of new update for your honor phone.

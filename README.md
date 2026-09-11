# Honor Tools

A collection of tools for exploring Honor devices (particularly VER-N49 - Honor Magic V2 & V5), but
could be useful for anyone who have honor device.

* XDA-Developers forum V2: https://xdaforums.com/t/root-on-honor-magic-v2.4679495/
* XDA-Developers forum V5: https://xdaforums.com/t/perfect-setup-for-ghostlock-runtime-root.4800809/

## HonorSuite patcher

Scripts to override HonorSuite binaries to allow mitmproxy to intercept the requests and see what
kind of url's & parameters it's using. You will also need [MITMProxy](https://mitmproxy.org/) and
[Proxifier](https://www.proxifier.com/) to properly redirect the HonorSuite requests.

How to setup interceptor: https://xdaforums.com/t/op11-edl-downloadtool-to-restore-your-device-to-oxygenos-coloros.4607995/

Also please check the scripts headers in the directory to get a clue how to use them. The produced
patched files are not replacing HonorSuite files to make it happy with checksums.

## Crawler for update.hihonorcdn.com

* XDA-Developers forum: https://xdaforums.com/t/unlock-bootloader-code-for-honor-magic-v2-root-with-magisk.4663415/post-89499716

Allows to get all the xml files from update.hihonorcdn.com and find versions of update zip files to
simplify your search of new update for your honor phone.

## collect_fastboot_adb_info.py

Script collects important data from fastboot and adb for honor devices to easily compare differences
between the states.

## honor_ouc_check.py

Script allows to get the next update hops for your device model directly from Honor Cloud. The only
issue is that it needs your extracted PKI from oeminfo of the device, which is not that easy to do.

I got my PKI via zygote-injection available on 8.0.0.105 - setting com.hihonor.ouc as a target you
can communicate by `com.hihonor.android.os.ProtectAreaEx.readProtectArea` and dump the data from
oeminfo.

WARNING: Applicable to Honor Magic V2 8.0.0.105

Details: [[honor_ouc_check.md]]

## honor_collect_logs_root.sh

The script reads different partitions on Honor device to collect all sorts of boot logs (including
xbl/abl/tz/kmsg etc). Previously we had to trigger kernel panic to allow hilogcat-early to collect
those in /data/vendor/log/reliability/dumplog directory, but now we can collect them live from
almost the same spots.

WARNING: Was checked only on Honor Magic V5 9.0.1.160

WARNING: Requires at least runtime root for execution (for example via https://github.com/YuKongA/ghostlock-app)

## himntn_rawdump_root.py

Honor uses special raw field called `himntn` in the beginning of rawdump partition, this script
reads it and gives details about the switches. Also it helps to prepare command to modify the
switches by using adb command - just prints out the command for the user.

WARNING: Was checked only on Honor Magic V5 9.0.1.160

WARNING: Requires at least runtime root for execution (for example via https://github.com/YuKongA/ghostlock-app)

Details: [[himntn_rawdump_root.md]]

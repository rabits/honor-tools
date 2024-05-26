#!/usr/bin/env python3
# Patch for HonorSuite to trust any certificate.
# It's second script in a chain - first one is 01_httpcomponent-patcher.py
#
# Usage:
# $ 02_honorsuite-patcher.py <HonorSuite dir>
#
# Script will produce 2 files: HonorSuits.exe and CommBaze.dll which will need to be copied into
# the original HonorSuite directory together with httpcomponenb.dll. After that you can kill the
# original HonorSuite.exe and run instead HonorSuits.exe with mitmproxy.

import os, sys

def patcher_replace(find_data, replace_data, file_data):
    pos = file_data.find(find_data)
    if pos == -1:
        return False
    for i in range(len(replace_data)):
        file_data[pos + i] = replace_data[i]
    return True

def patch_honorsuite(honorsuite_dir):
    # Patch HonorSuite.exe
    # Replaces link to httpcomponent.dll to httpcomponenb.dll to keep the checksum happy with original file
    find_data =    b'httpcomponent.dll'
    replace_data = b'httpcomponenb.dll'

    # Replaces link to CommBase.dll to CommBaze.dll to keep the checksum happy with original file
    find_data2 =    b'CommBase.dll'
    replace_data2 = b'CommBaze.dll'

    with open(os.path.join(honorsuite_dir, "HonorSuite.exe"), 'rb') as f:
        file_data = bytearray(f.read())
    if patcher_replace(find_data, replace_data, file_data) and patcher_replace(find_data2, replace_data2, file_data):
        with open("HonorSuits.exe", 'wb') as f:
            f.write(file_data)
        print("Patched HonorSuite.exe and stored as HonorSuits.exe")
    else:
        print("Error patching HonorSuite.exe")

    # Patch CommBase.dll
    with open(os.path.join(honorsuite_dir, "CommBase.dll"), 'rb') as f:
        file_data = bytearray(f.read())
    if patcher_replace(find_data, replace_data, file_data):
        with open("CommBaze.dll", 'wb') as f:
            f.write(file_data)
        print("Patched CommBase.dll and stored as CommBaze.dll")
    else:
        print("Error patching CommBase.dll")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: not enough params provided")
        sys.exit(1)

    patch_honorsuite(sys.argv[1])

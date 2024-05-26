#!/usr/bin/env python3
# Patch for HonorSuite to trust mitmproxy certificate.
# After executing of this script you need to run 02_honorsuite-patcher.py,
# which will modify HonorSuite.exe & CommBase.dll to link the right libraries
#
# Usage:
# $ ./01_httpcomponent-patcher.py <httpcomponent.dll> <cert.crt>
#   * <httpcomponent.dll> - path to file httpcomponent.dll of HonorSuite
#   * <cert.crt> - the CA certificate of mitmproxy (you can find it in ~/.mitmproxy/mitmproxy-ca-cert.pem)
#
# After patching the script will produce httpcomponenb.dll, needed to be copied to the original
# HonorSuite directory together with HonorSuits.exe & CommBaze.dll produced by 02_honorsuite-patcher.py.

import sys

BUFFER_SIZE = 32*1024  # Have to be bigger then regular certificate size
CERT_BEGIN = "-----BEGIN CERTIFICATE-----".encode()
CERT_END = "-----END CERTIFICATE-----".encode()

def patch_httpcomponent(dll_path, cert_path):
    with open(cert_path, 'rb') as f:
        new_crt_data = f.read()
    new_crt_size = len(new_crt_data)

    # Let's copy the binary file and replace the first fit certificate with provided one
    old_data = bytes()
    # The name httpcomponenb.dll is intentionnaly changed - to keep the checksum happy
    with open(dll_path, 'rb') as in_file, open("httpcomponenb.dll", 'wb') as out_file:
        crt_start_pos = 0
        crt_end_pos = 0
        crt_replaced = False
        while True:
            new_data = in_file.read(BUFFER_SIZE)
            combined = old_data+new_data
            while not crt_replaced:
                start_pos = combined.find(CERT_BEGIN, crt_end_pos-out_file.tell() if crt_end_pos > 0 else 0)
                if start_pos == -1:
                    break
                # Found cert beginning, let's find the end
                end_pos = combined.find(CERT_END, start_pos)
                if end_pos == -1:
                    # Cert start was found, but the end is not here, leaving for the next round
                    break

                crt_start_pos = out_file.tell() + start_pos
                crt_end_pos = out_file.tell() + end_pos + len(CERT_END)
                crt_size = crt_end_pos - crt_start_pos
                print("Found cert in position {}-{} size: {}b".format(crt_start_pos, crt_end_pos, crt_size))
                if new_crt_size <= crt_size:
                    print("Replacing found certificate by the new one: {}b".format(new_crt_size))

                    # We need to add zeroes in the end of the new cert to fit the size of old cert
                    new_crt_data += b"\0"*(crt_size-new_crt_size)
                    combined = combined[:start_pos] + new_crt_data + combined[end_pos+len(CERT_END):]
                    old_data = combined[:BUFFER_SIZE]
                    new_data = combined[BUFFER_SIZE:]
                    crt_replaced = True
                    break

            out_file.write(old_data)
            if not new_data:
                break
            old_data = new_data

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: not enough params provided")
        sys.exit(1)

    patch_httpcomponent(sys.argv[1], sys.argv[2])

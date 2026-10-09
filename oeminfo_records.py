#!/usr/bin/env python3
"""
Parse / safely patch a few Honor oeminfo records from an *unpacked* directory
produced by oeminfo_tool.py.

Records covered
  * DEBUG_LOCK_POLICY  (v8 12 / v6 67 / ABL 0x43) — hisecd STP status_v2
  * PSID_DATA          (v8 18 / v6 87 / NVE+ProtectArea "PSID_DATA")
  * FACINFO_LOCK_FLAGS (v8 1504 / v6 26) — factory LT/PT/UT station tokens
  * FRP_AUTH           (v8 1521 / v6 99) — dump only (ABL oem frp-unlock)

None of these three editable cells is in oeminfo_nvm_server's HMAC allow-list
(76/77/78/142/1502/1519). Writing them through HwOemInfoCustEx /
ProtectAreaEx stores the bytes as-is. Factory RSA-3072 tails are NOT
recomputed by the framework. hisecd will rewrite ID 12 on the next boot from
live kernel STP state.

Usage:
  ./oeminfo_records.py dump DIR
  ./oeminfo_records.py debug-lock DIR [--set NAME=SAFE|RISK] [--credible NAME=Y|N]
  ./oeminfo_records.py facinfo DIR [--set LT=P|F] [--set PT=P|F] [--set UT=P|F]
  ./oeminfo_records.py psid DIR
  ./oeminfo_records.py frp DIR
"""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DEBUG_LOCK_V8 = 12
DEBUG_LOCK_V6 = 67
PSID_V8 = 18
PSID_V6 = 87
FACINFO_V8 = 1504
FACINFO_V6 = 26
FRP_V8 = 1521
FRP_V6 = 99

ITEM_SIZE = 32
HEADER_SIZE = 0x40
# Factory SetFacInfoFlagToOeminfo writes snprintf("%s %s", station, P|F)
# at a byte offset in the 0x80 ASCII map. Tokens on this unit:
FACINFO_TOKENS = {
    "LT": 0x46,  # line test; GetFacInfo11
    "PT": 0x5A,  # product test; GetFacInfo11
    "UT": 0x6E,  # user test; GetFacInfo12 starts at 0x68
    "MT": 0x41,  # SetTestResult(testid=4) "MT %s"
}

# stp.conf / scd.conf / ABL status_v2 item ids
KNOWN_ITEMS: Dict[int, str] = {
    0x0001: "usb-debug",
    0x0200: "verifyboot",
    0x0201: "verity-enable",
    0x0202: "key-files",
    0x0203: "verified-state",
    0x0206: "fblock",
    0x0207: "userlock",
    0x0208: "check-su",
    0x0280: "eima",
    0x0282: "kcode",
    0x0283: "kcode-syscall",
    0x0284: "se-hook",
    0x0285: "mrcinfo",
    0x0300: "root-prop",
    0x0305: "sysrw",
    0x0380: "setids",
    0x0383: "se-enforcing",
    0x0385: "root-procs",
    0x0400: "firstrun",
}


def _find_payload(unpacked: Path, v8_id: int, prefer_active: bool = True) -> Path:
    suffix = "_active_data" if prefer_active else "_inactive_data"
    hits = sorted(unpacked.glob(f"{v8_id}_*{suffix}.*"))
    hits = [p for p in hits if p.suffix in {".bin", ".txt"}]
    if not hits:
        hits = sorted(unpacked.glob(f"{v8_id}_*_data.*"))
        hits = [p for p in hits if p.suffix in {".bin", ".txt"}]
    if not hits:
        raise FileNotFoundError(f"no unpacked payload for id {v8_id} in {unpacked}")
    return hits[0]


def _backup(path: Path) -> Path:
    dest = path.with_suffix(path.suffix + ".bak")
    if not dest.exists():
        shutil.copy2(path, dest)
    return dest


def _ts(unix: int) -> str:
    if not unix:
        return "0"
    try:
        return datetime.fromtimestamp(unix, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    except (OverflowError, OSError, ValueError):
        return str(unix)


# --- DEBUG_LOCK_POLICY -------------------------------------------------------

def parse_debug_lock(data: bytes) -> Dict:
    if len(data) < HEADER_SIZE:
        raise ValueError(f"DEBUG_LOCK too short: {len(data)}")
    magic, hdr_b, change_time, _pad, count = struct.unpack_from("<IIIII", data, 0)
    version = data[0x38:0x3C].split(b"\x00", 1)[0].decode("ascii", "replace")
    items = []
    for i in range(count):
        off = HEADER_SIZE + i * ITEM_SIZE
        rec = data[off:off + ITEM_SIZE]
        if len(rec) < ITEM_SIZE:
            break
        item_id = struct.unpack_from("<I", rec, 0)[0]
        flags = list(rec[4:8])
        name = rec[8:24].split(b"\x00", 1)[0].decode("ascii", "replace")
        time_u32 = struct.unpack_from("<I", rec, 24)[0]
        # ABL FUN_0006ee60: byte[5]=old, byte[6]=current; 1 => RISK, else SAFE.
        # byte[4] non-zero => credible Y (except fblock/userlock overlay from RAM).
        current_risk = flags[2] == 1
        old_risk = flags[1] == 1
        items.append({
            "index": i,
            "id": item_id,
            "id_hex": f"0x{item_id:04X}",
            "name": name,
            "category": item_id >> 8,
            "flags": flags,
            "status": "RISK" if current_risk else "SAFE",
            "old_status": "RISK" if old_risk else "SAFE",
            "credible": "Y" if flags[0] != 0 else "N",
            "time": time_u32,
            "time_utc": _ts(time_u32),
        })
    return {
        "hdr_a": magic,
        "hdr_b": hdr_b,
        "change_time": change_time,
        "change_time_utc": _ts(change_time),
        "count": count,
        "version": version,
        "payload_len": len(data),
        "items": items,
    }


def _set_item_flag(data: bytearray, item: Dict, status: Optional[str], credible: Optional[str]) -> None:
    off = HEADER_SIZE + item["index"] * ITEM_SIZE
    flags = bytearray(data[off + 4:off + 8])
    if status is not None:
        status = status.upper()
        if status not in {"SAFE", "RISK"}:
            raise ValueError("status must be SAFE or RISK")
        # current at [2]; keep old at [1] as previous current
        flags[1] = flags[2]
        flags[2] = 1 if status == "RISK" else 0
        struct.pack_into("<I", data, off + 24, int(datetime.now(tz=timezone.utc).timestamp()))
    if credible is not None:
        credible = credible.upper()
        if credible not in {"Y", "N", "YES", "NO"}:
            raise ValueError("credible must be Y or N")
        flags[0] = 0 if credible in {"N", "NO"} else 1
    data[off + 4:off + 8] = flags


def cmd_debug_lock(unpacked: Path, sets: List[str], credibles: List[str], write: bool) -> int:
    path = _find_payload(unpacked, DEBUG_LOCK_V8)
    data = bytearray(path.read_bytes())
    parsed = parse_debug_lock(bytes(data))
    print(f"# DEBUG_LOCK_POLICY  file={path.name}  v8={DEBUG_LOCK_V8} v6={DEBUG_LOCK_V6}")
    print(f"# version={parsed['version']} count={parsed['count']} "
          f"change_time={parsed['change_time_utc']}")
    print(f"# ABL: fastboot oem lock-state info  (common_oeminfo_read 0x43)")
    print(f"# Writer: vendor/bin/hisecd  (rmt_oeminfo_write, unsigned)")
    print()
    print(f"{'name':<16} {'id':<8} {'status':<6} {'old':<6} {'cred':<4} time")
    by_name = {}
    for it in parsed["items"]:
        by_name[it["name"]] = it
        print(f"{it['name']:<16} {it['id_hex']:<8} {it['status']:<6} "
              f"{it['old_status']:<6} {it['credible']:<4} {it['time_utc']}")

    patches: List[Tuple[str, Optional[str], Optional[str]]] = []
    for spec in sets:
        if "=" not in spec:
            raise ValueError(f"bad --set {spec}")
        name, val = spec.split("=", 1)
        patches.append((name, val, None))
    for spec in credibles:
        if "=" not in spec:
            raise ValueError(f"bad --credible {spec}")
        name, val = spec.split("=", 1)
        patches.append((name, None, val))

    if not patches:
        return 0
    if not write:
        print("\n(dry-run: pass --write to patch the unpacked file)")
        return 0

    for name, status, cred in patches:
        if name not in by_name:
            raise KeyError(f"unknown item {name!r}; known: {sorted(by_name)}")
        _set_item_flag(data, by_name[name], status, cred)
        # refresh name map after mutation so subsequent patches see new flags
        parsed = parse_debug_lock(bytes(data))
        by_name = {it["name"]: it for it in parsed["items"]}

    bak = _backup(path)
    path.write_bytes(data)
    print(f"\nWrote {path} (backup {bak.name})")
    print("Note: hisecd re-scans /proc/kernel_stp on boot and will rewrite this blob.")
    return 0


# --- PSID_DATA ----------------------------------------------------------------

def parse_psid(data: bytes) -> Dict:
    runs = []
    i = 0
    while i < len(data):
        if data[i] == 0:
            i += 1
            continue
        j = i
        while j < len(data) and data[j] != 0:
            j += 1
        runs.append({"off": i, "len": j - i, "hex": data[i:j].hex()})
        i = j
    return {"len": len(data), "nonzero_runs": runs}


def cmd_psid(unpacked: Path, replace: Optional[str], write: bool) -> int:
    path = _find_payload(unpacked, PSID_V8)
    data = bytearray(path.read_bytes())
    p = parse_psid(bytes(data))
    print(f"# PSID_DATA  file={path.name}  v8={PSID_V8} v6={PSID_V6}")
    print("# ProtectArea key PSID_DATA / HwReadOeminfoNve(\"PSID_DATA\")")
    print("# libgeneral_jni nativeReadProtectArea logs PSID_READ_OK")
    print(f"# length={p['len']}  (no RSA tail, not in HMAC allow-list)")
    for r in p["nonzero_runs"]:
        print(f"  run@0x{r['off']:03x} len={r['len']:3} {r['hex']}")
    print("\nNo public field layout: Honor treats this as an opaque product-security")
    print("identifier. Replacing bytes is stored as-is (unsigned), but anything that")
    print("hashes PSID (cloud/warranty/deviceauth) will disagree with the certs.")
    print("Keep length 290. Prefer ProtectArea name PSID_DATA over numeric IDs.")
    if not replace:
        return 0
    raw = Path(replace).read_bytes()
    if len(raw) != len(data):
        raise ValueError(f"replacement is {len(raw)} bytes, unpacked cell is {len(data)}")
    if not write:
        print(f"dry-run: would replace {path.name} with {replace} ({len(raw)} bytes)")
        return 0
    bak = _backup(path)
    path.write_bytes(raw)
    print(f"Wrote {path} (backup {bak.name})")
    return 0


# --- FACINFO_LOCK_FLAGS -------------------------------------------------------

def _ascii_slice(data: bytes, start: int, end: int) -> str:
    return "".join(chr(b) if 32 <= b < 127 else "." for b in data[start:end])


def parse_facinfo(data: bytes) -> Dict:
    stations = []
    for name, off in FACINFO_TOKENS.items():
        token = data[off:off + 4]
        token_s = token.decode("ascii", "replace").rstrip(" \x00")
        stations.append({"name": name, "offset": off, "token": token_s})
    return {
        "len": len(data),
        "stations": stations,
        "facinfo11": _ascii_slice(data, 0, 0x68).rstrip(),
        "facinfo12": _ascii_slice(data, 0x68, 0x80).rstrip(),
    }


def _print_facinfo(path: Path, data: bytes) -> None:
    parsed = parse_facinfo(data)
    print(f"# FACINFO_LOCK_FLAGS  file={path.name}  v8={FACINFO_V8} v6={FACINFO_V6}")
    print("# lib_factory_interface GetFacInfo11FromOeminfo / GetFacInfo12FromOeminfo")
    print("#   HalOeminfoRead(v6 0x1A); FacInfo11 = first 0x68, FacInfo12 = 24B @ 0x68")
    print("# SetFacInfoFlagToOeminfo(offset, station, P|F) via rmt_oeminfo_write(0x1A)")
    print("# SetTestResult(4) writes \"MT %s\" at 0x41. P=pass F=fail. Not a bootloader lock.")
    print(f"# FacInfo11[0:0x68]={parsed['facinfo11']!r}")
    print(f"# FacInfo12[0x68:0x80]={parsed['facinfo12']!r}")
    for s in parsed["stations"]:
        print(f"  {s['name']:<3} @ 0x{s['offset']:02x} token={s['token']!r}")


def cmd_facinfo(unpacked: Path, sets: List[str], write: bool, inactive: bool) -> int:
    path = _find_payload(unpacked, FACINFO_V8, prefer_active=not inactive)
    data = bytearray(path.read_bytes())
    _print_facinfo(path, bytes(data))
    alt = _find_payload(unpacked, FACINFO_V8, prefer_active=inactive)
    if alt != path:
        print()
        _print_facinfo(alt, alt.read_bytes())

    if not sets:
        return 0
    for spec in sets:
        if "=" not in spec:
            raise ValueError(f"bad --set {spec}")
        name, val = spec.split("=", 1)
        name = name.upper()
        val = val.upper()
        if name not in FACINFO_TOKENS:
            raise KeyError(f"station {name} not in {list(FACINFO_TOKENS)}")
        if len(val) == 1:
            token = f"{name} {val}"
        else:
            token = val
        token = token[:4].ljust(4)
        off = FACINFO_TOKENS[name]
        if not write:
            print(f"dry-run: {name} -> {token!r} at 0x{off:x} in {path.name}")
            continue
        data[off:off + 4] = token.encode("ascii")
        print(f"set {name} -> {token!r}")
    if write and sets:
        bak = _backup(path)
        path.write_bytes(data)
        print(f"Wrote {path} (backup {bak.name})")
    elif sets:
        print("pass --write to patch")
    return 0


# --- FRP_AUTH (dump only) -----------------------------------------------------

def parse_frp(data: bytes) -> Dict:
    if len(data) < 0x4C + 384:
        raise ValueError(f"FRP_AUTH unexpected size {len(data)} (want 460)")
    tag_len = struct.unpack_from("<H", data, 0)[0]
    data_len = struct.unpack_from("<H", data, 0x22)[0]
    version = struct.unpack_from("<H", data, 0x46)[0]
    rsa_bits = struct.unpack_from("<H", data, 0x4A)[0]
    tag = data[2:2 + min(tag_len, 32)]
    body = data[0x24:0x24 + min(data_len, 32)]
    return {
        "len": len(data),
        "tag_len": tag_len,
        "tag_hex": tag.hex(),
        "data_len": data_len,
        "data_ascii": body.decode("ascii", "replace"),
        "data_hex": body.hex(),
        "kdf_u16_0x44": struct.unpack_from("<H", data, 0x44)[0],
        "version": version,
        "u16_0x48": struct.unpack_from("<H", data, 0x48)[0],
        "rsa_bits": rsa_bits,
        "sig_len": len(data) - 0x4C,
        "sig_sha256_prefix": data[0x4C:0x4C + 8].hex(),
    }


def cmd_frp(unpacked: Path) -> int:
    path = _find_payload(unpacked, FRP_V8)
    p = parse_frp(path.read_bytes())
    print(f"# FRP_AUTH  file={path.name}  v8={FRP_V8} v6={FRP_V6}  size={p['len']}")
    print("# ABL oem_frp_check_password: common_oeminfo_read(99), require version==3")
    print("# then password_check (data@0x24 + u16@0x44), TAG compare (32B @ +2),")
    print("# then RSA-3072 PSS over prefix + reconstructed 0x4a header.")
    print("# fastboot: oem frp-unlock  (16-byte ASCII/hex password argument)")
    print("# Separate path oem flash:frp-erase verifies a signed package, then")
    print("# erases the FRP *partition*, not this cell.")
    print(json.dumps({k: p[k] for k in p if k != "sig_sha256_prefix"}, indent=2))
    print(f"sig[0:8]={p['sig_sha256_prefix']}  rsa_bits={p['rsa_bits']}  version={p['version']}")
    print("\nThis tool will not modify FRP_AUTH: the 384-byte tail is a factory")
    print("RSA-3072 signature. oeminfo_nvm_server / hisecd / ProtectAreaEx will")
    print("not re-sign it. A patched blob fails ABL TAG/PSS checks.")
    return 0


def cmd_dump(unpacked: Path) -> int:
    cmd_debug_lock(unpacked, [], [], write=False)
    print()
    cmd_facinfo(unpacked, [], write=False, inactive=False)
    print()
    cmd_psid(unpacked, replace=None, write=False)
    print()
    try:
        cmd_frp(unpacked)
    except FileNotFoundError as e:
        print(f"# FRP_AUTH not present: {e}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_dump = sub.add_parser("dump", help="print all four records")
    p_dump.add_argument("dir")

    p_dl = sub.add_parser("debug-lock", help="dump / patch DEBUG_LOCK_POLICY items")
    p_dl.add_argument("dir")
    p_dl.add_argument("--set", action="append", default=[], metavar="NAME=SAFE|RISK")
    p_dl.add_argument("--credible", action="append", default=[], metavar="NAME=Y|N")
    p_dl.add_argument("--write", action="store_true")

    p_fi = sub.add_parser("facinfo", help="dump / patch LT/PT/UT/MT tokens")
    p_fi.add_argument("dir")
    p_fi.add_argument("--set", action="append", default=[], metavar="LT=P|F")
    p_fi.add_argument("--inactive", action="store_true", help="patch the inactive copy")
    p_fi.add_argument("--write", action="store_true")

    p_ps = sub.add_parser("psid", help="dump PSID_DATA")
    p_ps.add_argument("dir")
    p_ps.add_argument("--replace", metavar="FILE", help="raw 290-byte replacement")
    p_ps.add_argument("--write", action="store_true")

    p_frp = sub.add_parser("frp", help="dump FRP_AUTH (read-only)")
    p_frp.add_argument("dir")

    args = ap.parse_args(argv)
    unpacked = Path(args.dir)
    if not unpacked.is_dir():
        print(f"not a directory: {unpacked}", file=sys.stderr)
        return 2
    try:
        if args.cmd == "dump":
            return cmd_dump(unpacked)
        if args.cmd == "debug-lock":
            return cmd_debug_lock(unpacked, args.set, args.credible, args.write)
        if args.cmd == "facinfo":
            return cmd_facinfo(unpacked, args.set, args.write, args.inactive)
        if args.cmd == "psid":
            return cmd_psid(unpacked, args.replace, args.write)
        if args.cmd == "frp":
            return cmd_frp(unpacked)
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

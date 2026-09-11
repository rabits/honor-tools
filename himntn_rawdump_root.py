#!/usr/bin/env python3
"""Read Honor Magic V5 HIMNTN from rawdump (or a hex dump) and emit a dd patch.

WARNING: Applicable to Honor Magic V5 9.0.1.160

The script never writes to the device. --enable/--disable only print the
resulting mask and a copy-paste adb command.

Per-item boot effects (ABL → cmdline → init): see himntn_rawdump.md.

Storage (ABL HimntnAbl.c / xmntn HimntnPartWrite):
  /dev/block/by-name/rawdump offset 0, 8 bytes little-endian u64
  stored = (48-bit mask) | 0x4849000000000000   # ASCII "HI" in bits 48..63
  ABL then applies  stored & 0xB7B6FFFFFFFFFFFF  to recover the mask.

  Item n is enabled iff bit (47-n) of the mask is set
  (CmdHimntnItemSwitch: (mask << n) >> 47 & 1).

Other rawdump users in UNPACKED_ROM_V5_9.0.1.160 (not HIMNTN bits):
  ABL          — HIMNTN RMW; rainbow reason at +8; ABL log at 0x84000
  xmntn        — -h 1 RMW of HIMNTN on non-commercial; -r 1 copies
                 ramdump slices (xbl_abl @0x80000, last_kmsg @0x200000, ...)
  recovery / factory_reset — DoDisableHimntn during factory reset
  rainbow.ko   — rb_header.himntn_data in reserved RAM (mirror, not the NV)
  qcom-dload-mode.ko + persist.vendor.sys.rawdump_copy — eMMC ramdump payload
  xbl_ramdump  — reads board id from rawdump
  hiview       — uploads xmntn-copied dumplog/*/rawdump.bin (file, not the block)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from base64 import b64encode
from typing import Iterable

MAGIC = 0x4849000000000000
MAGIC_MASK = 0x4849000000000000
STRIP_MAGIC = 0xB7B6FFFFFFFFFFFF  # ABL: stored & this after magic check
ITEM_COUNT = 48
HI_LE_SUFFIX = bytes.fromhex("4948")  # last two bytes of stored u64 in memory

# ABL consumers (RainbowLib/HimntnAbl.c on this device). invert=True means the
# named *effect* is active when the HIMNTN item bit is 0.
ITEMS: dict[str, dict] = {
    "factory_marker": {
        "item": 1,
        "invert": False,
        "effect": "xmntn treats the partition as already programmed; skips factory default rewrite on non-commercial builds",
        "when_on": "HimntnPartWrite is skipped (log: partition has been correct)",
        "when_off": "non-commercial xmntn -h 1 may overwrite the mask with a factory default",
        "risk": "medium",
    },
    "tologpart": {
        "item": 3,
        "invert": False,
        "effect": "ABL appends androidboot.log.tologpart=1",
        "when_on": "androidboot.log.tologpart=1",
        "when_off": "no extra tologpart token",
        "risk": "low",
    },
    "labexternal": {
        "item": 4,
        "invert": False,
        "effect": "ABL sets androidboot.labexternal",
        "when_on": "androidboot.labexternal=true",
        "when_off": "androidboot.labexternal=false",
        "risk": "high",
    },
    "serial_bypass": {
        "item": 7,
        "invert": False,
        "effect": "ABL ReadSerialNum / BootDetector path (skip some SN sources when set)",
        "when_on": "serial-number lookup may skip fallbacks",
        "when_off": "normal serial lookup",
        "risk": "high",
    },
    "maxcpus_2": {
        "item": 8,
        "invert": False,
        "effect": "ABL appends maxcpus=2",
        "when_on": "maxcpus=2 (limits the kernel to 2 CPUs)",
        "when_off": "all CPUs stay available",
        "risk": "high",
    },
    "on_failure_panic": {
        "item": 9,
        "invert": True,
        "effect": "ABL appends OnFailurePanic when the item bit is OFF",
        "when_on": "OnFailurePanic is on cmdline (kernel panics on some failures)",
        "when_off": "no OnFailurePanic token",
        "risk": "high",
    },
    "fastboot_gate": {
        "item": 10,
        "invert": False,
        "effect": "ABL fastboot dispatcher uses this around battery/command gating",
        "when_on": "item 10 set (DAT_001d3484 inverted in ABL)",
        "when_off": "item 10 clear",
        "risk": "high",
    },
    "uart_earlycon": {
        "item": 22,
        "invert": False,
        "effect": "ABL appends msm_geni_serial / console=ttyMSM0 / earlycon (chip-specific table); also required for logcat_kmsg",
        "when_on": "UART/earlycon tokens added",
        "when_off": "serial console extras omitted (or the disabled-table string)",
        "risk": "high",
    },
    "log_buf_len_4m": {
        "item": 28,
        "invert": False,
        "effect": "ABL appends log_buf_len=4M (overrides DTB log_buf_len=1M)",
        "when_on": "log_buf_len=4M — larger printk ring, early kmsg survives longer",
        "when_off": "kernel keeps DTB 1M buffer; dmesg wraps and drops early boot",
        "risk": "low",
    },
    "printk_devkmsg": {
        "item": 29,
        "invert": True,
        "effect": "ABL appends printk.devkmsg=on when the item bit is OFF",
        "when_on": "printk.devkmsg=on (userspace can read /dev/kmsg without rate limit)",
        "when_off": "default printk.devkmsg rate limit",
        "risk": "low",
    },
    "boot_detector": {
        "item": 31,
        "invert": False,
        "effect": "ABL BootDetector extra path together with serial_bypass",
        "when_on": "BootDetector extra handling enabled",
        "when_off": "BootDetector extra handling skipped unless serial_bypass is on",
        "risk": "medium",
    },
    "logcat_kmsg_b2": {
        "item": 40,
        "invert": False,
        "effect": "bit2 of androidboot.logcat.kmsg index (needs uart_earlycon)",
        "when_on": "contributes 4 to logcat.kmsg selector",
        "when_off": "selector bit2 clear",
        "risk": "medium",
    },
    "logcat_kmsg_b1": {
        "item": 41,
        "invert": False,
        "effect": "bit1 of androidboot.logcat.kmsg index (needs uart_earlycon)",
        "when_on": "contributes 2 to logcat.kmsg selector",
        "when_off": "selector bit1 clear",
        "risk": "medium",
    },
    "logcat_kmsg_b0": {
        "item": 42,
        "invert": False,
        "effect": "bit0 of androidboot.logcat.kmsg index (needs uart_earlycon)",
        "when_on": "contributes 1 to logcat.kmsg selector",
        "when_off": "selector bit0 clear",
        "risk": "medium",
    },
    "console_level_b3": {
        "item": 43,
        "invert": False,
        "effect": "bit3 of androidboot.console.level",
        "when_on": "contributes 8 to console.level",
        "when_off": "level bit3 clear",
        "risk": "medium",
    },
    "console_level_b2": {
        "item": 44,
        "invert": False,
        "effect": "bit2 of androidboot.console.level",
        "when_on": "contributes 4 to console.level",
        "when_off": "level bit2 clear",
        "risk": "medium",
    },
    "console_level_b1": {
        "item": 45,
        "invert": False,
        "effect": "bit1 of androidboot.console.level",
        "when_on": "contributes 2 to console.level",
        "when_off": "level bit1 clear",
        "risk": "medium",
    },
    "console_level_b0": {
        "item": 46,
        "invert": False,
        "effect": "bit0 of androidboot.console.level",
        "when_on": "contributes 1 to console.level",
        "when_off": "level bit0 clear",
        "risk": "medium",
    },
}

ALIASES = {
    "log_buf_len": "log_buf_len_4m",
    "log_buf_len=4m": "log_buf_len_4m",
    "log_buf_len_4mb": "log_buf_len_4m",
    "4m": "log_buf_len_4m",
    "4mb": "log_buf_len_4m",
    "uart": "uart_earlycon",
    "earlycon": "uart_earlycon",
    "devkmsg": "printk_devkmsg",
    "printk.devkmsg": "printk_devkmsg",
    "onfailurepanic": "on_failure_panic",
    "maxcpus": "maxcpus_2",
    "lab": "labexternal",
}


def item_bit(item: int) -> int:
    if not 0 <= item < ITEM_COUNT:
        raise ValueError(f"HIMNTN item {item} out of range 0..47")
    return 47 - item


def item_is_set(mask: int, item: int) -> bool:
    return bool((mask >> item_bit(item)) & 1)


def set_item(mask: int, item: int, enabled: bool) -> int:
    bit = item_bit(item)
    if enabled:
        return mask | (1 << bit)
    return mask & ~(1 << bit)


def stored_from_mask(mask: int) -> int:
    return (mask & ((1 << 48) - 1)) | MAGIC


def mask_from_stored(stored: int) -> int:
    if ((stored ^ 0xFFFFFFFFFFFFFFFF) & MAGIC_MASK) != 0:
        raise ValueError(
            f"HIMNTN magic missing in stored 0x{stored:016x} "
            "(expected high bits 0x4849). Refusing to decode."
        )
    return stored & STRIP_MAGIC & ((1 << 48) - 1)


def bitmap48(mask: int) -> str:
    return "".join("1" if item_is_set(mask, i) else "0" for i in range(ITEM_COUNT))


def le_bytes(stored: int) -> bytes:
    return stored.to_bytes(8, "little")


def stored_to_mem_hex(stored: int) -> str:
    return le_bytes(stored).hex()


def parse_from_hex(text: str) -> tuple[int, int, str]:
    """Return (mask, stored, how_parsed)."""
    raw = text.strip().lower().replace("0x", "").replace(" ", "").replace(":", "")
    if not re.fullmatch(r"[0-9a-f]+", raw) or len(raw) % 2:
        raise ValueError(f"not a hex HIMNTN value: {text!r}")
    blob = bytes.fromhex(raw)

    if len(blob) == 8 and blob[6:8] == HI_LE_SUFFIX:
        stored = int.from_bytes(blob, "little")
        return mask_from_stored(stored), stored, "8-byte little-endian dump (memory order)"

    value = int(raw, 16)
    if (value & MAGIC_MASK) == MAGIC:
        return mask_from_stored(value), value, "stored u64 with HI magic"
    if value <= 0xFFFFFFFFFFFF:
        stored = stored_from_mask(value)
        return value, stored, "48-bit HIMNTN mask"
    raise ValueError(
        f"cannot interpret 0x{value:x}: not a 48-bit mask and no HI magic"
    )


def adb_cmd(adb: str, *args: str) -> bytes:
    proc = subprocess.run(
        [adb, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"{' '.join([adb, *args])} failed ({proc.returncode}): {err}")
    return proc.stdout


def read_from_device(adb: str) -> tuple[int, int, dict[str, str]]:
    blob = adb_cmd(
        adb,
        "exec-out",
        "su",
        "-c",
        "dd if=/dev/block/by-name/rawdump bs=8 count=1 2>/dev/null",
    )
    if len(blob) < 8:
        raise RuntimeError(f"rawdump read returned {len(blob)} bytes, expected 8")
    stored = int.from_bytes(blob[:8], "little")
    mask = mask_from_stored(stored)
    extra: dict[str, str] = {}
    try:
        cmdline = adb_cmd(adb, "exec-out", "su", "-c", "cat /proc/cmdline").decode(
            "utf-8", "replace"
        )
        extra["cmdline"] = cmdline.replace("\r", " ").strip()
        m = re.search(r"HIMNTN=(0x[0-9A-Fa-f]+)", cmdline)
        extra["cmdline_himntn"] = m.group(1) if m else ""
        m = re.search(r"log_buf_len=(\S+)", cmdline)
        extra["cmdline_log_buf_len"] = m.group(1) if m else ""
    except RuntimeError:
        pass
    return mask, stored, extra


def resolve_name(name: str) -> str:
    key = name.strip().lower().replace("-", "_")
    if key in ALIASES:
        key = ALIASES[key]
    if key in ITEMS:
        return key
    m = re.fullmatch(r"(?:item_)?(0x[0-9a-f]+|\d+)$", key)
    if m:
        item = int(m.group(1), 0)
        for n, meta in ITEMS.items():
            if meta["item"] == item:
                return n
        raise ValueError(f"item {item} has no friendly name; known: {', '.join(ITEMS)}")
    raise ValueError(f"unknown parameter {name!r}. known: {', '.join(ITEMS)}")


def desired_item_bit(name: str, want_effect_on: bool) -> bool:
    meta = ITEMS[name]
    if meta["invert"]:
        return not want_effect_on
    return want_effect_on


def apply_changes(mask: int, enable: Iterable[str], disable: Iterable[str]) -> int:
    out = mask
    for name in enable:
        key = resolve_name(name)
        out = set_item(out, ITEMS[key]["item"], desired_item_bit(key, True))
    for name in disable:
        key = resolve_name(name)
        out = set_item(out, ITEMS[key]["item"], desired_item_bit(key, False))
    return out


def emit_dd(stored: int) -> str:
    # base64 so the payload is safe inside single-quoted su -c (no \x quoting traps).
    b64 = b64encode(le_bytes(stored)).decode("ascii")
    inner = (
        "set -e; "
        "BLK=/data/local/tmp/himntn_blk.bin; "
        "dd if=/dev/block/by-name/rawdump of=$BLK bs=512 count=1; "
        f"echo {b64} | base64 -d | dd of=$BLK bs=1 count=8 conv=notrunc; "
        "dd if=$BLK of=/dev/block/by-name/rawdump bs=512 count=1 conv=notrunc; "
        "sync; "
        "dd if=/dev/block/by-name/rawdump bs=8 count=1 2>/dev/null | od -An -tx1"
    )
    return f"adb exec-out su -c '{inner}'"


def name_for_item(item: int) -> str | None:
    for name, meta in ITEMS.items():
        if meta["item"] == item:
            return name
    return None


def print_report(mask: int, stored: int, source: str, extra: dict[str, str] | None = None) -> None:
    extra = extra or {}
    print(f"source:              {source}")
    print(f"stored u64:          0x{stored:016x}")
    print(f"memory bytes (LE):   0x{stored_to_mem_hex(stored)}")
    print(f"HIMNTN mask:         0x{mask:x}")
    print(f"48-bit bitmap:       {bitmap48(mask)}")
    print(f"fastboot write form: HIMNTN@{bitmap48(mask)}")
    cmd_h = extra.get("cmdline_himntn")
    if cmd_h:
        same = cmd_h.lower() == f"0x{mask:x}"
        print(f"cmdline HIMNTN:      {cmd_h}  ({'matches rawdump' if same else 'DIFFERS from rawdump — reboot needed or ABL did not apply'})")
    if extra.get("cmdline_log_buf_len"):
        print(f"cmdline log_buf_len: {extra['cmdline_log_buf_len']}")
    print()
    print("known ABL effects")
    print("-" * 88)
    for name, meta in ITEMS.items():
        bit_on = item_is_set(mask, meta["item"])
        effect_on = (not bit_on) if meta["invert"] else bit_on
        state = "ON " if effect_on else "off"
        inv = "  [inverted item]" if meta["invert"] else ""
        print(
            f"  {name:<18} item=0x{meta['item']:02x}({meta['item']:2d})  "
            f"bit={int(bit_on)}  effect={state}{inv}"
        )
        print(f"      {meta['effect']}")
        print(f"      now: {meta['when_on'] if effect_on else meta['when_off']}")
    print()
    print("raw items without an ABL string on this ROM (do not flip blindly)")
    unknown_on = [i for i in range(ITEM_COUNT) if item_is_set(mask, i) and name_for_item(i) is None]
    unknown_off = [i for i in range(ITEM_COUNT) if not item_is_set(mask, i) and name_for_item(i) is None]
    print(f"  ON : {unknown_on or '-'}")
    print(f"  off: {unknown_off or '-'}")


def print_patch(old_mask: int, new_mask: int) -> None:
    if old_mask == new_mask:
        print("no bit changes; nothing to write")
        return
    old_s = stored_from_mask(old_mask)
    new_s = stored_from_mask(new_mask)
    print()
    print("computed write (script does NOT apply it)")
    print("-" * 88)
    print(f"  old mask   0x{old_mask:x}")
    print(f"  new mask   0x{new_mask:x}")
    print(f"  old stored 0x{old_s:016x}   mem 0x{stored_to_mem_hex(old_s)}")
    print(f"  new stored 0x{new_s:016x}   mem 0x{stored_to_mem_hex(new_s)}")
    print(f"  new bitmap {bitmap48(new_mask)}")
    print()
    print("changed effects:")
    for name, meta in ITEMS.items():
        before = item_is_set(old_mask, meta["item"])
        after = item_is_set(new_mask, meta["item"])
        if before == after:
            continue
        be = (not before) if meta["invert"] else before
        ae = (not after) if meta["invert"] else after
        print(f"  {name}: {'ON' if be else 'off'} -> {'ON' if ae else 'off'}  ({meta['when_on'] if ae else meta['when_off']})")
    print()
    print("RMW of the first 512-byte block of rawdump (HIMNTN is only the first 8 bytes).")
    print("A ramdump/dload can later overwrite offset 0; factory reset runs DoDisableHimntn.")
    print()
    print(emit_dd(new_s))
    print()
    print("After reboot, confirm:  adb exec-out su -c \"tr ' ' '\\n' < /proc/cmdline | grep -E 'HIMNTN|log_buf_len'\"")


def check_collect(mask: int, extra: dict[str, str]) -> int:
    bit = item_is_set(mask, ITEMS["log_buf_len_4m"]["item"])
    live = extra.get("cmdline_log_buf_len", "")
    print(f"  HIMNTN mask 0x{mask:x}  (rawdump 0x{stored_to_mem_hex(stored_from_mask(mask))})")
    print(f"  rawdump log_buf_len_4m: {'ON' if bit else 'OFF'}")
    print(f"  this-boot cmdline log_buf_len: {live or '(unknown)'}")
    if bit and live == "4M":
        print("  printk ring is 4M on this boot — early kmsg is much less likely to wrap away.")
        return 0
    if bit and live != "4M":
        print("  rawdump already has 4M, but this boot still has the DTB 1M buffer.")
        print("  Reboot once, then collect, to get the larger ring.")
        return 0
    print()
    print("  Kernel printk is still 1M (DTB). After a few minutes of uptime dmesg")
    print("  starts in the middle of boot (~6s+ / after wrap even later).")
    print("  Enable HIMNTN log_buf_len_4m, reboot, then collect:")
    print()
    new = apply_changes(mask, ["log_buf_len_4m"], [])
    print("    ./himntn_rawdump.py --enable log_buf_len_4m")
    print()
    print("  " + emit_dd(stored_from_mask(new)))
    print()
    print("  Collect will continue anyway so you can still grab XBL/ABL logs.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Inspect Honor HIMNTN in rawdump and print a dd command (never writes)."
    )
    p.add_argument("--adb", default="adb", help="adb binary (default: adb)")
    p.add_argument(
        "--from",
        dest="from_hex",
        metavar="HEX",
        help='HIMNTN value instead of adb: memory dump (0x00fef6851c404948), mask (0x401C85F6FE00), or stored u64',
    )
    p.add_argument("--enable", action="append", default=[], metavar="NAME", help="turn an effect on (repeatable)")
    p.add_argument("--disable", action="append", default=[], metavar="NAME", help="turn an effect off (repeatable)")
    p.add_argument("--list", action="store_true", help="list known parameter names and exit")
    p.add_argument(
        "--check-collect",
        action="store_true",
        help="preflight for collect_current_boot_logs.sh (recommend 4M if unset)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.list:
        for name, meta in ITEMS.items():
            inv = " inverted" if meta["invert"] else ""
            print(f"{name:18} item=0x{meta['item']:02x}{inv}  {meta['effect']}")
        print("aliases:", ", ".join(f"{k}->{v}" for k, v in ALIASES.items()))
        return 0

    extra: dict[str, str] = {}
    if args.from_hex:
        mask, stored, how = parse_from_hex(args.from_hex)
        source = f"--from ({how})"
    else:
        try:
            mask, stored, extra = read_from_device(args.adb)
        except Exception as exc:
            print(f"failed to read rawdump via adb: {exc}", file=sys.stderr)
            print("pass a hex dump with --from 0x00fef6851c404948", file=sys.stderr)
            return 1
        source = "adb exec-out su -c dd .../rawdump"

    if args.check_collect:
        return check_collect(mask, extra)

    print_report(mask, stored, source, extra)
    if args.enable or args.disable:
        try:
            new_mask = apply_changes(mask, args.enable, args.disable)
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 2
        print_patch(mask, new_mask)
    return 0


if __name__ == "__main__":
    sys.exit(main())

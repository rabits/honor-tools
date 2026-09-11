#!/usr/bin/env python3
"""
Collect detailed device information via fastboot and adb.
Output: Markdown to stdout for line-by-line diff comparison.

Usage:
  ./collect.py                          # prompt fastboot -> adb, wait for device
  ./collect.py SERIAL                   # same, filter by serial
  ./collect.py SERIAL fastboot          # fastboot phase only
  ./collect.py SERIAL adb               # adb phase only (append to existing dump)

When `adb shell su` works (KernelSU/Magisk), root is auto-detected and an extra
## ADB (root) section is collected. Use --no-root to disable, --root to warn if missing.

Safe on locked devices: read-only getvar/oem queries only.
Dangerous commands are listed at the end of the fastboot section as comments.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import shlex
import subprocess
import sys
import time
from typing import List, Optional, Sequence, Tuple

SDK = os.environ.get("ANDROID_SDK", "/opt/android/sdk")
FASTBOOT = os.environ.get("FASTBOOT", f"{SDK}/platform-tools/fastboot")
ADB = os.environ.get("ADB", f"{SDK}/platform-tools/adb")

WAIT_TIMEOUT_S = int(os.environ.get("COLLECT_WAIT_TIMEOUT", "600"))
POLL_INTERVAL_S = 2.0


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def run(
    argv: Sequence[str],
    timeout: int = 120,
) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(
            list(argv),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"TIMEOUT after {timeout}s: {' '.join(argv)}"
    except FileNotFoundError:
        return 127, "", f"command not found: {argv[0]}"


def md_heading(level: int, title: str) -> None:
    print(f"{'#' * level} {title}\n")


def md_command_block(cmd_display: str, output: str) -> None:
    print(f"$ `{cmd_display}`")
    print("```")
    if output:
        print(output.rstrip())
    print("```\n")


def fastboot_argv(serial: Optional[str], *args: str) -> List[str]:
    cmd = [FASTBOOT]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(args)
    return cmd


def adb_argv(serial: Optional[str], *args: str) -> List[str]:
    cmd = [ADB]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(args)
    return cmd


def fastboot_cmd(serial: Optional[str], *args: str, timeout: int = 120) -> str:
    code, out, err = run(fastboot_argv(serial, *args), timeout=timeout)
    parts: List[str] = []
    if out:
        parts.append(out.rstrip())
    if err:
        parts.append(err.rstrip())
    if code != 0 and not parts:
        parts.append(f"exit code {code}")
    return "\n".join(parts)


def adb_shell(
    serial: Optional[str],
    command: str,
    timeout: int = 300,
    root: bool = False,
) -> str:
    if root:
        argv = adb_argv(serial, "shell", "su", "-c", command)
    else:
        argv = adb_argv(serial, "shell", command)
    code, out, err = run(argv, timeout=timeout)
    parts: List[str] = []
    if out:
        parts.append(out.rstrip())
    if err:
        parts.append(err.rstrip())
    if code != 0 and not parts:
        parts.append(f"exit code {code}")
    return "\n".join(parts)


def detect_root(serial: str) -> Tuple[bool, str]:
    """Return (has_root, details) from `su -c id`."""
    out = adb_shell(serial, "id", timeout=30, root=True)
    if "uid=0" in out and "root" in out:
        return True, out.strip()
    return False, out.strip()


def list_fastboot_serials() -> List[str]:
    code, out, _ = run([FASTBOOT, "devices"], timeout=30)
    if code != 0:
        return []
    serials: List[str] = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "fastboot":
            serials.append(parts[0])
    return serials


def list_adb_serials() -> List[str]:
    code, out, _ = run([ADB, "devices"], timeout=30)
    if code != 0:
        return []
    serials: List[str] = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            serials.append(parts[0])
    return serials


def wait_for_fastboot(serial: Optional[str], timeout_s: int = WAIT_TIMEOUT_S) -> str:
    return serial
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        serials = list_fastboot_serials()
        if serial:
            if serial in serials:
                return serial
        elif serials:
            return serials[0]
        time.sleep(POLL_INTERVAL_S)
    raise SystemExit(
        f"Timeout: no fastboot device found"
        + (f" with serial {serial}" if serial else "")
    )


def wait_for_adb(serial: Optional[str], timeout_s: int = WAIT_TIMEOUT_S) -> str:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        serials = list_adb_serials()
        if serial:
            if serial in serials:
                return serial
        elif serials:
            return serials[0]
        time.sleep(POLL_INTERVAL_S)
    raise SystemExit(
        f"Timeout: no adb device found"
        + (f" with serial {serial}" if serial else "")
    )


def prompt_continue(message: str) -> None:
    eprint(message)
    eprint("Press Enter when ready...")
    try:
        input()
    except EOFError:
        pass


# --- Fastboot: safe read-only queries (verified on locked VER-N49 / MBH-N49) ---

FASTBOOT_GETVARS: List[str] = [
  # Standard
    "product",
    "variant",
    "secure",
    "unlocked",
    "serialno",
    "version-bootloader",
    "version-baseband",
    "max-download-size",
    "battery-voltage",
    "battery-soc",
    "current-slot",
    "slot-count",
    "slot-successful:_a",
    "slot-successful:_b",
    "slot-unbootable:_a",
    "slot-unbootable:_b",
    "slot-retry-count:_a",
    "slot-retry-count:_b",
    "has-slot:boot",
    "has-slot:system",
    "has-slot:vendor",
    "has-slot:product",
    "has-slot:vbmeta",
    "has-slot:recovery",
    "has-slot:init_boot",
    "has-slot:vendor_boot",
    # Honor / rescue
    "devicemodel",
    "vendorcountry",
    "rescue_version",
    "rescue_ugs_port",
    "rescue_get_hwid",
    "rescue_get_updatetoken",
    "system_update_state",
    "dongle_info",
    "get_battery_status",
    # May attempt rescue boot path — included in manual dumps; usually returns status only
    #"rescue_enter_recovery",
    # Often missing on some builds
    "rescue_phoneinfo",
    "error_print",
    "is-userspace",
]

FASTBOOT_PARTITION_SIZES: List[str] = [
    "boot",
    "init_boot",
    "vendor_boot",
    "recovery",
    "vbmeta",
    "abl",
    "xbl",
    "modem",
    "dsp",
    "dtbo",
    "userdata",
    "metadata",
    "frp",
    "persist",
    "super",
    "cust",
    "version",
    "patch_hn",
    "eng_system",
    "eng_vendor",
]

FASTBOOT_OEM_COMMANDS: List[str] = [
    "lock-state info",
    "battery_present_check",
    "get-product-model",
    "get-bootinfo",
    "check-rootinfo",
    "get_hwnff_ver",
    "get-build-number",
    "oeminforead-BASE_VERSION",
    "oeminforead-CUSTOM_VERSION",
    "oeminforead-PRELOAD_VERSION",
    "oeminforead-ANDROID_VERSION",
    "oeminforead-GROUP_VERSION",
    "oeminforead-FAC_PRODUCT_VER",
    "oeminforead-hotainfo",
]

# Not executed — reference / manual testing only
FASTBOOT_DANGEROUS_COMMANDS: List[str] = [
    "fastboot flashing unlock",
    "fastboot flashing unlock_critical",
    "fastboot flashing lock",
    "fastboot flashing lock_critical",
    "fastboot erase <partition>",
    "fastboot format <partition>",
    "fastboot flash <partition> <image>",
    "fastboot wipe",
    "fastboot oem unlock",
    "fastboot oem frp-unlock",
    "fastboot oem edl",
    "fastboot oem dump-storage",
    "fastboot oem dump-storage rrecord",
    "fastboot oem oeminforeusederase",
    "fastboot oem oeminfoerase",
    "fastboot oem erase-boardid",
    "fastboot oem set-boardid",
    "fastboot oem set-hw-fence-value",
    "fastboot oem set-dg-img",
    "fastboot oem set-dg-img-resume",
    "fastboot oem set-gpu-preemption",
    "fastboot oem off-mode-charge",
    "fastboot oem append-cmdline",
    "fastboot oem crash",
    "fastboot oem shutdown",
    "fastboot oem hwdog certify set",
    "fastboot oem hwdog certify enc begin",
    "fastboot oem hwdog certify close",
    "fastboot reboot-bootloader",
    "fastboot reboot-fastboot",
    "fastboot reboot recovery",
    "fastboot reboot emergency",
]

# OEM strings present in abl.pe but blocked or unknown on locked device — skipped at runtime
FASTBOOT_OEM_BLOCKED_REFERENCE: List[str] = [
    "get-bsn",
    "get-sn",
    "get-psn",
    "getqsn",
    "device-info",
    "storage_info",
    "get_ufs_info",
    "get-boardid",
    "dump_reboot_recovery",
    "dump_auto_reboot",
    "himntn",
    "edl",
    "uart",
    "log",
    "logcat2kmsg",
    "console_level",
    "disable-charger-screen",
    "enable-charger-screen",
    "audio-framework",
    "bootfail",
    "bootfail_partition_cmds",
    "bootfail_package_name",
    "dump-storage",
    "oeminforeusedread",
    "oeminforeusederase",
    "getencryptsn",
    "getencryptudid",
    "getencryptimei",
    "get_socid",
    "get-custom-c-version",
    "get-encrypt-device-certificate",
    "get-encrypt-key-attestation",
    "emmc-dump",
    "emmc_diag",
    "check-image",
    "get_key_version",
    "get-drop-info",
    "device info",
    "oeminforead",
    "mrc-info",
    "custom-stateinfo",
    "labexternal",
    "select-display-panel",
    "applogtologpart",
    "upsigndata-ask-material",
    "batterycheck",
]


def collect_fastboot(serial: str) -> None:
    md_heading(2, "Fastboot")

    md_heading(3, "fastboot devices")
    md_command_block("fastboot devices", fastboot_cmd(None, "devices"))

    for var in FASTBOOT_GETVARS:
        display = f"fastboot getvar {var}"
        md_command_block(display, fastboot_cmd(serial, "getvar", var))

    md_heading(3, "partition-size")
    for part in FASTBOOT_PARTITION_SIZES:
        var = f"partition-size:{part}"
        display = f"fastboot getvar {var}"
        md_command_block(display, fastboot_cmd(serial, "getvar", var))

    md_heading(3, "partition-type")
    for part in FASTBOOT_PARTITION_SIZES:
        var = f"partition-type:{part}"
        display = f"fastboot getvar {var}"
        md_command_block(display, fastboot_cmd(serial, "getvar", var))

    md_heading(3, "oem commands (safe read-only)")
    for oem in FASTBOOT_OEM_COMMANDS:
        display = f"fastboot oem {oem}"
        md_command_block(display, fastboot_cmd(serial, "oem", oem))

    md_heading(3, "Dangerous / blocked commands (NOT executed)")
    print("```")
    for line in FASTBOOT_DANGEROUS_COMMANDS:
        print(f"# {line}")
    print("```\n")

    md_heading(3, "OEM commands blocked on locked device (NOT executed, from abl.pe)")
    print("```")
    for oem in FASTBOOT_OEM_BLOCKED_REFERENCE:
        print(f"# fastboot oem {oem}")
    print("```\n")


# --- ADB shell commands ---

ADB_SHELL_COMMANDS: List[Tuple[str, str, int]] = [
    ("ls -al /dev/block/by-name/ /dev/block/mapper", "ls -al /dev/block/by-name/ /dev/block/mapper", 120),
    ("ls -alh /dev/block/by-name", "ls -alh /dev/block/by-name", 120),
    ("ls -alh /dev/block/mapper", "ls -alh /dev/block/mapper", 120),
    ("df", "df", 60),
    ("cat /proc/mounts", "cat /proc/mounts", 60),
    ("cat /proc/version", "cat /proc/version", 30),
    ("cat /proc/cpuinfo", "cat /proc/cpuinfo", 30),
    ("cat /proc/meminfo | head -40", "cat /proc/meminfo | head -40", 30),
    ("uname -a", "uname -a", 30),
    ("getevent -lp 2>/dev/null || getevent -l", "getevent -l", 30),
    ("hwnff get_hwnff_ver", "hwnff get_hwnff_ver", 30),
    ("hwnff get_battery_temp", "hwnff get_battery_temp", 30),
    ("hwnff get_battery_voltage", "hwnff get_battery_voltage", 30),
    ("hwnff get_root_status", "hwnff get_root_status", 30),
    ("hwnff get_security_status", "hwnff get_security_status", 60),
    ("hwnff get_physical_number", "hwnff get_physical_number", 30),
    ("hwnff get_platform", "hwnff get_platform", 30),
    ("lpdump /dev/block/by-name/super", "lpdump /dev/block/by-name/super", 180),
    ("ls -al /sys/class/block", "ls -al /sys/class/block", 60),
]

ADB_GETPROP_KEYS: List[str] = [
    "ro.product.model",
    "ro.product.device",
    "ro.product.name",
    "ro.product.brand",
    "ro.product.manufacturer",
    "ro.build.fingerprint",
    "ro.build.display.id",
    "ro.build.version.release",
    "ro.build.version.sdk",
    "ro.build.version.security_patch",
    "ro.build.version.incremental",
    "ro.build.description",
    "ro.build.tags",
    "ro.build.type",
    "ro.build.id",
    "ro.build.user",
    "ro.build.host",
    "ro.build.date",
    "ro.build.date.utc",
    "ro.boot.serialno",
    "ro.serialno",
    "ro.bootmode",
    "ro.boot.verifiedbootstate",
    "ro.boot.vbmeta.device_state",
    "ro.boot.flash.locked",
    "ro.secure",
    "ro.debuggable",
    "ro.adb.secure",
    "ro.crypto.state",
    "ro.crypto.type",
    "ro.hardware",
    "ro.board.platform",
    "ro.soc.model",
    "ro.soc.manufacturer",
    "ro.baseband",
    "ro.bootloader",
    "ro.vendor.build.fingerprint",
    "ro.odm.build.fingerprint",
    "ro.system.build.fingerprint",
    "ro.product.build.fingerprint",
    "ro.vendor.build.security_patch",
    "ro.mediatek.version.release",
    "gsm.version.baseband",
    "gsm.version.ril-impl",
    "persist.sys.usb.config",
    "sys.usb.state",
    "dev.mnt.blk.data",
    "dev.mnt.dev.data",
]


# Root-only commands (verified on MBH-N49 + KernelSU)
ADB_ROOT_COMMANDS: List[Tuple[str, str, int]] = [
    # KernelSU / root manager
    ("/data/adb/ksud --version 2>/dev/null || ksud --version 2>/dev/null", "ksud --version", 30),
    ("ls -laR /data/adb 2>/dev/null", "ls -laR /data/adb", 30),
    ("/data/adb/ksu/bin/bootctl get-current-slot 2>/dev/null || bootctl get-current-slot 2>/dev/null", "bootctl get-current-slot", 30),
    ("/data/adb/ksu/bin/bootctl get-suffix 2>/dev/null || bootctl get-suffix 2>/dev/null", "bootctl get-suffix", 30),
    # Boot / kernel
    ("cat /proc/cmdline", "cat /proc/cmdline", 30),
    ("cat /proc/bootconfig", "cat /proc/bootconfig", 30),
    ("uname -a", "uname -a", 30),
    ("cat /proc/modules", "cat /proc/modules", 60),
    ("lsmod", "lsmod", 60),
    ("dmesg", "dmesg", 120),
    # SELinux / security
    ("getenforce", "getenforce", 15),
    ("cat /sys/fs/selinux/enforce", "cat /sys/fs/selinux/enforce", 15),
    ("cat /sys/fs/selinux/policyvers", "cat /sys/fs/selinux/policyvers", 15),
    ("cat /proc/keys", "cat /proc/keys", 30),
    ("cat /proc/sys/kernel/random/boot_id", "cat /proc/sys/kernel/random/boot_id", 15),
    # Device tree / SoC
    ("cat /proc/device-tree/model 2>/dev/null || cat /sys/firmware/devicetree/base/model", "device-tree model", 15),
    ("cat /sys/devices/soc0/machine 2>/dev/null; cat /sys/devices/soc0/family 2>/dev/null; cat /sys/devices/soc0/soc_id 2>/dev/null", "soc0 info", 15),
    # Block devices / partitions
    ("cat /proc/partitions", "cat /proc/partitions", 30),
    ("cat /proc/diskstats", "cat /proc/diskstats", 30),
    ("for p in abl boot init_boot vendor_boot recovery vbmeta modem dsp dtbo super metadata frp persist oeminfo devinfo; do echo -n \"$p: \"; blockdev --getsize64 /dev/block/by-name/$p 2>/dev/null || echo N/A; done", "blockdev partition sizes", 60),
    ("strings /dev/block/by-name/oeminfo 2>/dev/null | head -200", "strings oeminfo (head 200)", 60),
    ("xxd /dev/block/by-name/devinfo 2>/dev/null | head -32", "xxd devinfo (head 32)", 30),
    ("xxd /dev/block/by-name/frp 2>/dev/null | head -16", "xxd frp (head 16)", 30),
    ("blkid 2>/dev/null", "blkid", 60),
    ("cat /sys/block/dm-*/dm/name 2>/dev/null", "dm device names", 30),
    # Mounts / vendor persist
    ("mount", "mount", 60),
    ("ls -la /mnt/vendor/persist 2>/dev/null", "ls /mnt/vendor/persist", 30),
    ("find /mnt/vendor/persist -maxdepth 3 -type f 2>/dev/null | head -100", "persist files (head 100)", 60),
    # Build props (all partitions)
    ("for f in /system/build.prop /system_ext/etc/build.prop /vendor/build.prop /product/etc/build.prop /odm/etc/build.prop /vendor_dlkm/etc/build.prop /system_dlkm/etc/build.prop /vendor/odm_dlkm/etc/build.prop; do echo \"=== $f ===\"; cat \"$f\" 2>/dev/null || echo N/A; done", "all build.prop files", 60),
    # Thermal / power / CPU
    ("for z in /sys/class/thermal/thermal_zone*/type; do echo -n \"$(cat $z): \"; cat ${z%/type}/temp 2>/dev/null; done", "thermal zones", 30),
    ("cat /sys/class/power_supply/battery/uevent", "battery uevent", 15),
    ("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq 2>/dev/null", "cpu max freq", 15),
    ("cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null | sort -u", "cpu governors", 15),
    # Network
    ("ip addr", "ip addr", 30),
    ("ip route", "ip route", 30),
    ("ip -6 route", "ip -6 route", 30),
    ("iptables -L -n -v 2>/dev/null | head -80", "iptables (head 80)", 30),
    ("ss -tulpn 2>/dev/null", "ss -tulpn", 30),
    # Settings / system state
    ("settings list global", "settings list global", 120),
    ("settings list secure", "settings list secure", 120),
    ("settings list system", "settings list system", 120),
    # Recovery / OTA metadata
    ("ls -la /data/misc/recovery/ 2>/dev/null", "ls /data/misc/recovery", 15),
    ("cat /data/misc/recovery/ro.build.fingerprint 2>/dev/null", "recovery ro.build.fingerprint", 15),
    ("ls -la /data/system/ 2>/dev/null | head -60", "ls /data/system (head 60)", 30),
    ("wc -c /data/system/packages.xml 2>/dev/null", "packages.xml size", 15),
    # Fstab / audio
    ("ls /vendor/etc/fstab* 2>/dev/null; for f in /vendor/etc/fstab*; do echo \"=== $f ===\"; cat \"$f\" 2>/dev/null; done", "fstab", 30),
    ("cat /proc/asound/cards", "asound cards", 15),
    # Memory / kernel stats
    ("cat /proc/meminfo", "cat /proc/meminfo", 30),
    ("cat /proc/buddyinfo", "cat /proc/buddyinfo", 15),
    ("cat /proc/zoneinfo | head -60", "cat /proc/zoneinfo (head 60)", 30),
    ("cat /proc/interrupts | head -40", "cat /proc/interrupts (head 40)", 30),
    ("cat /proc/iomem | head -40", "cat /proc/iomem (head 40)", 30),
    # Honor vendor binaries
    ("ls -la /vendor/bin/ 2>/dev/null | grep -iE 'oem|hota|honor|hihonor|nff'", "vendor honor binaries", 30),
]

ADB_ROOT_DANGEROUS_COMMANDS: List[str] = [
    "dd if=/dev/block/by-name/<partition> of=/sdcard/dump.img",
    "echo > /dev/block/by-name/<partition>",
    "resetprop <key> <value>",
    "/data/adb/ksu/bin/bootctl set-active-boot-slot <slot>",
    "iptables -A/-D ...",
    "echo 1 > /sys/fs/selinux/enforce  # or disable",
    "rm -rf /data/...",
    "magisk --install-module ...",
]


def collect_adb_root(serial: str) -> None:
    md_heading(2, "ADB (root)")

    su = lambda cmd, timeout=300: adb_shell(serial, cmd, timeout=timeout, root=True)

    for shell_cmd, display, timeout in ADB_ROOT_COMMANDS:
        md_heading(3, display)
        md_command_block(
            f"adb -s {serial} shell su -c {shlex.quote(shell_cmd)}",
            su(shell_cmd, timeout),
        )

    md_heading(3, "Dangerous root commands (NOT executed)")
    print("```")
    for line in ADB_ROOT_DANGEROUS_COMMANDS:
        print(f"# {line}")
    print("```\n")


def collect_adb(serial: str, use_root: Optional[bool] = None) -> None:
    has_root, root_details = detect_root(serial)
    if use_root is False:
        has_root = False
    elif use_root is True and not has_root:
        eprint("Warning: --root requested but `su` is not available; continuing without root.")

    md_heading(2, "ADB")

    md_heading(3, "root detection")
    md_command_block(
        f"adb -s {serial} shell su -c 'id'",
        root_details if root_details else "(no output)",
    )
    print(f"- root available: **{'yes' if has_root else 'no'}**\n")

    md_heading(3, "adb devices")
    code, out, err = run(adb_argv(None, "devices"), timeout=30)
    md_command_block("adb devices", (out or "") + (err or ""))

    shell_fn = lambda cmd, timeout=300: adb_shell(serial, cmd, timeout, root=has_root)

    for shell_cmd, display, timeout in ADB_SHELL_COMMANDS:
        md_heading(3, display)
        prefix = f"adb -s {serial} shell su -c {shlex.quote(shell_cmd)}" if has_root else f"adb -s {serial} shell {display}"
        md_command_block(prefix, shell_fn(shell_cmd, timeout))

    md_heading(3, "getprop (selected)")
    for key in ADB_GETPROP_KEYS:
        val = shell_fn(f"getprop {key}", 30)
        md_command_block(f"getprop {key}", val)

    md_heading(3, "getprop (full)")
    md_command_block("getprop", shell_fn("getprop", timeout=300))

    md_heading(3, "pm")
    for pm_cmd in [
        "pm list features",
        "pm list hwfeatures",
        "pm list instrumentation",
        "pm list packages -f -a --show-versioncode",
    ]:
        md_command_block(pm_cmd, shell_fn(pm_cmd, timeout=600))

    md_heading(3, "dumpsys (selected)")
    for svc in [
        "battery",
        "display",
        "telephony.registry",
        "package",
        "user",
        "activity",
    ]:
        cmd = f"dumpsys {svc}"
        md_command_block(cmd, shell_fn(cmd, timeout=300))

    md_heading(3, "service list")
    md_command_block("service list", shell_fn("service list", timeout=120))

    if has_root:
        collect_adb_root(serial)


def print_header(serial: Optional[str], phase: str, root: Optional[bool] = None) -> None:
    now = dt.datetime.now(dt.timezone.utc).astimezone()
    md_heading(1, f"Device collect — {phase}")
    print(f"- timestamp: {now.isoformat(timespec='seconds')}")
    if serial:
        print(f"- serial: {serial}")
    if root is not None:
        print(f"- root: {'yes' if root else 'no'}")
    print(f"- fastboot: {FASTBOOT}")
    print(f"- adb: {ADB}")
    print()


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Collect device info via fastboot/adb as Markdown")
    parser.add_argument("serial", nargs="?", help="Device serial (fastboot/adb)")
    parser.add_argument(
        "protocol",
        nargs="?",
        choices=["fastboot", "adb"],
        help="fastboot or adb only; default runs both with prompts",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Do not wait for device if not present (fail immediately)",
    )
    parser.add_argument(
        "--root",
        action="store_true",
        help="Require root (warn if su unavailable; still collect non-root adb data)",
    )
    parser.add_argument(
        "--no-root",
        action="store_true",
        help="Never use su even if available",
    )
    args = parser.parse_args(argv)

    if args.root and args.no_root:
        parser.error("--root and --no-root are mutually exclusive")

    use_root: Optional[bool] = None
    if args.root:
        use_root = True
    elif args.no_root:
        use_root = False

    serial_hint = args.serial
    protocol = args.protocol

    if protocol == "fastboot":
        serial = serial_hint
        if not args.no_wait:
            if not serial_hint:
                prompt_continue("Reboot device into fastboot mode.")
            serial = wait_for_fastboot(serial_hint)
        print_header(serial, "fastboot")
        collect_fastboot(serial)
        return

    if protocol == "adb":
        serial = serial_hint
        if not args.no_wait:
            if not serial_hint:
                prompt_continue("Reboot device into HLOS (normal boot) with USB debugging enabled.")
            serial = wait_for_adb(serial_hint)
        has_root, _ = detect_root(serial)
        effective_root = has_root if use_root is not False else False
        print_header(serial, "adb", root=effective_root)
        collect_adb(serial, use_root=use_root)
        return

    # Both phases: interactive flow
    prompt_continue("Reboot device into fastboot mode.")
    fb_serial = wait_for_fastboot(serial_hint)
    print_header(fb_serial, "fastboot + adb")
    collect_fastboot(fb_serial)

    prompt_continue("Reboot device into HLOS (normal boot) with USB debugging enabled.")
    adb_serial = wait_for_adb(serial_hint or fb_serial)
    collect_adb(adb_serial, use_root=use_root)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Honor HnOUC baseline-version client (MagicOS 8 check, MagicOS 9 / Magic V5 authorize).

Check (same host the V2 client used; V5 BlRequest still posts types 2/3/4):

  POST https://update.platform.hihonorcloud.com/blversion/v1/version/check
  headers: x-productId, x-deviceDescId, x-devModel, x-requestId
           Content-Type: application/json; charset=UTF-8
           Accept-Encoding: identity
  body:    commonRules + versionPackageRules + deviceInfo
           (+ keyAttestation / deviceCertificate)

Authorize (HnOUC AuthHota → g2.d.e, then TokenHmac is removed before the POST):

  POST https://update.platform.hihonorcloud.com/blversion/v1/version/authorize
  body:    BlAuthParams (deviceCertificate, keyAttestation, deviceInfo,
           blVersions, deviceToken, updateToken, versionIdList, ver)

  deviceToken / updateToken / TokenHmac come from the phone:
  android.hnouc.HnOucNative.getUpdateAuthParams()
  The server echoes updateToken inside data=<base64>&sign=...
  That raw body is update_auth.sa; saveUpdateAuth writes the same bytes.
  The stock app also stores TokenHmac in oeminfo SYSTEM_UPDATE_AUTH_TOKEN.
  This script does not invent either value.

CDN: http://update.hihonorcdn.com/TDS/data/bl/files/v{id}/f1/full/filelist.xml
update.hihonorcdn.com is WAF-gated (HTTP 567 / 514 / 403 from this network).
Use the SOCKS5 proxy + Firefox UA that already works:

  --proxy socks5://127.0.0.1:1080
  --user-agent 'Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/144.0'

The check API returns the *next* hop for the current component versions, not a
full catalog. --walk follows that chain. A live current version that has an
update typically requires HnPKI; without it the server answers HTTP 401 / 101003731.

Examples:
  python3 honor_ouc_check.py --from-adb
  python3 honor_ouc_check.py --from-adb --walk --filelist \\
    --key-attestation pki_honor_magic_v5/key_attestation.txt \\
    --device-certificate pki_honor_magic_v5/device_certificate.txt

  # Next-hop packages from the check, tokens from the phone, .sa via JNI:
  python3 honor_ouc_check.py --from-adb --authorize --auth-target 10.0.0.122 --pull-auth-params \\
    --key-attestation pki_honor_magic_v5/key_attestation.txt \\
    --device-certificate pki_honor_magic_v5/device_certificate.txt \\
    --auth-out pki_honor_magic_v5/auth_out
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import re
import os
import stat
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from typing import Any

DEFAULT_PROXY = None
DEFAULT_UA = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/144.0"
)
CHECK_URL = "https://update.platform.hihonorcloud.com/blversion/v1/version/check"
AUTHORIZE_URL = "https://update.platform.hihonorcloud.com/blversion/v1/version/authorize"
CDN_HOST = "http://update.hihonorcdn.com"
CDN_PREFIX = "/TDS/data/bl/files"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JAVA = os.path.join(SCRIPT_DIR, "HnOucAuth.java")
PHONE_DEX = "/data/local/tmp/hnouc_auth.dex"

BL_INFO_KEYS = (
    "blVersionType",
    "laneId",
    "laneName",
    "currentBlVersionId",
    "currentBlVersionNumber",
    "targetBlVersionId",
    "targetBlVersionNumber",
    "updateAction",
    "targetCowCompressControl",
)
PKG_KEYS = ("versionId", "versionPackageType", "packageIndex")

PACKAGE_TYPE = {
    2: "base",
    3: "cust",
    4: "preload",
    5: "cota",
    13: "hotpatch",
    15: "para",
    17: "dcota",
}


def adb_getprop(name: str) -> str:
    r = subprocess.run(
        ["adb", "shell", "getprop", name],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if r.returncode != 0:
        raise RuntimeError(f"adb getprop {name} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def curl(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    proxy: str | None,
    timeout: int,
    user_agent: str | None,
) -> tuple[int, bytes]:
    cmd = ["curl", "-sS", "--max-time", str(timeout), "-w", "\n%{http_code}"]
    if proxy:
        cmd += ["--proxy", proxy]
    if method != "GET":
        cmd += ["-X", method]
    if user_agent:
        cmd += ["-H", f"User-Agent: {user_agent}"]
    for k, v in (headers or {}).items():
        cmd += ["-H", f"{k}: {v}"]
    if data is not None:
        cmd += ["--data-binary", "@-"]
    cmd.append(url)
    r = subprocess.run(cmd, input=data, capture_output=True, timeout=timeout + 5)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip() or f"curl exit {r.returncode}"
        raise RuntimeError(f"{err} ({url})")
    raw = r.stdout
    nl = raw.rfind(b"\n")
    if nl < 0:
        raise RuntimeError(f"curl produced no status line for {url}")
    try:
        status = int(raw[nl + 1 :])
    except ValueError as e:
        raise RuntimeError(f"bad curl status trailer: {raw[nl+1:]!r}") from e
    return status, raw[:nl]


def sale_info(
    vendor: str,
    country: str,
    magic: str,
    ram: str,
    emmc: str,
    cpu: str,
    client_name: str,
) -> str:
    # OemInfoUtil.getSaleInfo: A0|vendor|country|N|platform|ram|emmc|cpu|6hFlag|extra|client|V0
    return f"|{vendor}|{country}|N|{magic}|{ram}|{emmc}|{cpu}|Y||{client_name}|Y"


def fingerprint(model: str, incremental: str) -> str:
    return f"HONOR/{model}/HNVER:14/HONOR{model}/{incremental}:user/release-keys"


def version_number(explicit: str, fallback: str) -> str:
    return explicit or fallback


def build_check_body(args: argparse.Namespace) -> dict[str, Any]:
    incremental = f"{args.base_version}{args.cust}E2R2P2"
    base_number = version_number(
        getattr(args, "base_version_number", ""),
        f"{args.lgrp} {args.base_version}".strip(),
    )
    cust_number = version_number(
        getattr(args, "cust_version_number", ""),
        f"{args.model}-CUST {args.cust_version}({args.cust})",
    )
    preload_number = version_number(
        getattr(args, "preload_version_number", ""),
        f"{args.model}-PRELOAD {args.preload_version}({args.cust}R2)",
    )
    finger = args.fingerprint or fingerprint(args.model, incremental)
    rules: list[dict[str, Any]] = [
        {"versionPackageType": 2, "versionNumber": base_number},
        {"versionPackageType": 3, "versionNumber": cust_number},
        {"versionPackageType": 4, "versionNumber": preload_number},
    ]
    if args.patch_version:
        rules.append({"versionPackageType": 13, "versionNumber": args.patch_version})
    if args.cota_version:
        rules.append(
            {
                "versionPackageType": 5,
                "versionNumber": args.cota_version,
                "rules": {"appInfos": [], "cotaAppListVersion": "R0", "iconDpi": "480"},
            }
        )
    body: dict[str, Any] = {
        "commonRules": {
            "platformVersion": args.platform_version,
            "gmsVersion": args.gms_version,
            "updateAction": args.action,
            "updateType": 1,
            "networkType": 2,
            "clientType": "hnouc",
            "clientVersion": args.client_version,
            "dVersion": args.d_version,
            "cVersion": args.c_version or args.cust,
            "currentTime": int(time.time() * 1000),
            "devModel": args.model,
            "fingerPrint": finger,
            "language": args.language,
            "os": args.os,
            "subGroup": "",
            "verGroup": "",
            "vnKey": ";",
            "saleInfo": sale_info(
                args.vendor, args.country, args.software_platform,
                args.ram, args.emmc, args.cpu, args.client_name,
            ),
            "vendorCountry": args.vendor_country or f"{args.country}_{args.vendor}",
            "boardID": args.board_id,
            "softwarePlatform": args.software_platform,
            "usageInfo": "error",
            "plmn": "0",
            "deviceType": "PHONE",
            "checkMode": args.check_mode,
            "verifyInfo": json.dumps(
                {"data": "Y", "hwInit": "Y", "hota": "Y|Y|Y", "payCenter": "Y", "verNum": "N"},
                separators=(",", ":"),
            ),
            "logOnly": args.log_only,
        },
        "versionPackageRules": rules,
        "deviceInfo": {"deviceId": args.device_id, "udid": args.udid},
        "cotaInfo": {"vendorCota": "", "country": "DEFAULT", "vendorExpiredTime": 0},
        "lastFailStatus": [],
    }
    if args.key_attestation:
        body["keyAttestation"] = PathText(args.key_attestation)
    if args.device_certificate:
        body["deviceCertificate"] = PathText(args.device_certificate)
    return body


def PathText(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def check_headers(args: argparse.Namespace) -> dict[str, str]:
    return {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
        "x-productId": "SmartPhone",
        "x-deviceDescId": args.device_id,
        "x-devModel": args.model,
        "x-requestId": str(uuid.uuid4()),
    }


def version_check(args: argparse.Namespace, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    payload = json.dumps(body, separators=(",", ":")).encode()
    status, raw = curl(
        CHECK_URL,
        method="POST",
        headers=check_headers(args),
        data=payload,
        proxy=args.proxy,
        timeout=args.timeout,
        user_agent=args.check_user_agent,
    )
    try:
        parsed = json.loads(raw.decode("utf-8", "replace") or "{}")
    except json.JSONDecodeError:
        parsed = {"_raw": raw.decode("utf-8", "replace")}
    return status, parsed


def cdn_url(version_id: str, rel: str) -> str:
    return f"{CDN_HOST}{CDN_PREFIX}/v{version_id}/f1/{rel}"


def fetch_filelist(args: argparse.Namespace, version_id: str) -> dict[str, Any]:
    url = cdn_url(version_id, "full/filelist.xml")
    status, raw = curl(
        url,
        proxy=args.proxy,
        timeout=args.timeout,
        user_agent=args.user_agent,
        headers={"Accept-Encoding": "identity", "Connection": "keep-alive"},
    )
    out: dict[str, Any] = {"versionId": version_id, "url": url, "http": status}
    if status != 200:
        out["error"] = raw.decode("utf-8", "replace")[:300]
        return out
    root = ET.fromstring(raw)
    out["packageType"] = (root.findtext("packageType") or "").strip()
    out["packageSolution"] = (root.findtext("packageSolution") or "").strip()
    out["supportPKI"] = (root.findtext("supportPKI") or "").strip()
    vendor = root.find("vendorInfo")
    if vendor is not None:
        out["vendorPackage"] = vendor.attrib.get("package", "")
        out["vendorName"] = vendor.attrib.get("name", "")
    files = []
    for f in root.findall("files/file"):
        spath = (f.findtext("spath") or "").strip()
        size = int(f.findtext("size") or "0")
        sha = (f.findtext("sha256") or "").strip()
        files.append(
            {
                "name": spath,
                "size": size,
                "sha256": sha,
                "download": cdn_url(version_id, f"full/{spath}"),
            }
        )
    out["files"] = files
    vab = root.find("VirtualAB")
    if vab is not None:
        out["virtualAb"] = {
            "cowsize": vab.findtext("cowsize"),
            "fileSize": vab.findtext("fileSize"),
        }
    return out


def summarize_check(resp: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    result = resp.get("result") or {}
    hops = []
    for item in result.get("blVersionCheckResults") or []:
        info = item.get("blVersionInfo") or {}
        hop = {
            "status": item.get("status"),
            "blVersionType": item.get("blVersionType"),
            "current": info.get("currentBlVersionNumber"),
            "target": info.get("targetBlVersionNumber"),
            "lane": info.get("laneName"),
            "updateAction": info.get("updateAction"),
            "descriptPackageId": item.get("descriptPackageId"),
            "components": item.get("targetBlComponents") or [],
            "updatePackages": item.get("updatePackages") or [],
        }
        hops.append(hop)
    versions = result.get("versionList") or []
    return hops, versions


def adb_shell(command: str, *, root: bool = False, timeout: int = 20) -> str:
    if root:
        argv = ["adb", "exec-out", "su", "-c", command]
    else:
        argv = ["adb", "shell", command]
    r = subprocess.run(argv, capture_output=True, timeout=timeout)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(err or f"adb failed ({command})")
    return r.stdout.decode("utf-8", "replace")


def package_versions(package: str) -> tuple[str, str]:
    text = adb_shell(f"dumpsys package {package}")
    code = ""
    name = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("versionCode=") and not code:
            code = stripped.split("=", 1)[1].split()[0]
        elif stripped.startswith("versionName=") and not name:
            name = stripped.split("=", 1)[1].strip()
        if code and name:
            break
    return code, name


def prop_prefer(*names: str) -> str:
    for name in names:
        value = adb_getprop(name)
        if value:
            return value
    return ""


def apply_from_adb(args: argparse.Namespace) -> None:
    args.model = args.model or adb_getprop("ro.product.model")
    args.cust = args.cust or prop_prefer("ro.magic.cversion", "ro.product.CustCVersion")
    args.c_version = args.c_version or args.cust
    args.device_id = args.device_id or adb_getprop("ro.serialno")
    live_board = adb_getprop("ro.board.boardid")
    if live_board and args.board_id in ("", "8119"):
        args.board_id = live_board
    args.fingerprint = args.fingerprint or adb_getprop("ro.build.fingerprint")
    base = prop_prefer(
        "ro.comp.hl.product_base_version.real",
        "ro.comp.hl.product_base_version",
    )
    if base:
        args.base_version_number = args.base_version_number or base
        if " " in base:
            lgrp, ver = base.rsplit(" ", 1)
            args.lgrp = args.lgrp or lgrp
            args.base_version = args.base_version or ver
    cota = adb_getprop("msc.sys.defaultcotaversion")
    if cota:
        args.cota_version = args.cota_version or cota
    custv = prop_prefer(
        "ro.comp.hl.product_cust_version.real",
        "ro.comp.hl.product_cust_version",
    )
    if custv:
        args.cust_version_number = args.cust_version_number or custv
        if "(" in custv:
            left, _ = custv.split("(", 1)
            args.cust_version = args.cust_version or left.rsplit(" ", 1)[-1]
    pre = prop_prefer(
        "ro.comp.hl.product_preload_version.real",
        "ro.comp.hl.product_preload_version",
    )
    if pre:
        args.preload_version_number = args.preload_version_number or pre
        if "(" in pre:
            left, _ = pre.split("(", 1)
            args.preload_version = args.preload_version or left.rsplit(" ", 1)[-1]
    plat = adb_getprop("ro.build.version.magic")
    if plat:
        args.software_platform = args.software_platform or plat
        if plat.startswith("MagicOS_"):
            args.platform_version = args.platform_version or plat.split("_", 1)[1]
    args.gms_version = args.gms_version or adb_getprop("ro.com.google.gmsversion")
    custom = ""
    try:
        custom = adb_shell("head -n 1 /data/custom.bin", root=True).strip().splitlines()[0].strip()
    except (RuntimeError, subprocess.TimeoutExpired, IndexError):
        custom = ""
    if "/" in custom:
        # /data/custom.bin is vendor/country. The check body keeps that order,
        # with '/' replaced by '_': def/eea → def_eea.
        vendor, country = custom.split("/", 1)
        args.vendor = args.vendor or vendor
        args.country = args.country or country
        args.vendor_country = args.vendor_country or custom.replace("/", "_")
    else:
        vendorcountry = adb_getprop("ro.boot.vendorcountry") or adb_getprop("ro.product.VendorCountry")
        if "/" in vendorcountry:
            country, vendor = vendorcountry.split("/", 1)
            args.country = args.country or country
            args.vendor = args.vendor or vendor
            args.vendor_country = args.vendor_country or f"{args.country}_{args.vendor}"
    args.os = args.os or f"Android {adb_getprop('ro.build.version.release')}"
    if args.patch_version == "patch00":
        try:
            patch_prop = adb_shell("cat /patch_hn/patch.prop", root=True)
        except (RuntimeError, subprocess.TimeoutExpired):
            patch_prop = ""
        for line in patch_prop.splitlines():
            if line.startswith("ro.patchversion="):
                args.patch_version = line.split("=", 1)[1].strip() or "patch00"
                break
    try:
        code, name = package_versions("com.hihonor.ouc")
    except (RuntimeError, subprocess.TimeoutExpired):
        code, name = "", ""
    if code:
        args.client_version = code if args.client_version == "140100136" else args.client_version
    if name:
        args.client_name = name if args.client_name == "14.1.0.136" else args.client_name


def hop_component(hop: dict[str, Any], package_type: int) -> str:
    for comp in hop.get("components") or []:
        if comp.get("versionPackageType") == package_type:
            return str(comp.get("versionNumber") or "")
    return ""


def installed_key(args: argparse.Namespace) -> tuple[str, str, str, str]:
    return (
        getattr(args, "base_version_number", "") or f"{args.lgrp} {args.base_version}".strip(),
        getattr(args, "cust_version_number", ""),
        getattr(args, "preload_version_number", ""),
        args.patch_version,
    )


def full_hop_state(args: argparse.Namespace, hop: dict[str, Any]) -> dict[str, str] | None:
    """Next check position is the type-1 target of every component, not base alone."""
    if hop.get("blVersionType") not in (1, None):
        return None
    if hop.get("status") not in (0, "0", None):
        return None
    base = hop_component(hop, 2)
    if not base:
        return None
    return {
        "base_version_number": base,
        "base_version": base.rsplit(" ", 1)[-1],
        "lgrp": base.rsplit(" ", 1)[0] if " " in base else args.lgrp,
        "cust_version_number": hop_component(hop, 3) or getattr(args, "cust_version_number", ""),
        "preload_version_number": hop_component(hop, 4) or getattr(args, "preload_version_number", ""),
        "patch_version": args.patch_version,
    }


def apply_installed(args: argparse.Namespace, state: dict[str, str]) -> None:
    old_base = args.base_version
    args.base_version_number = state["base_version_number"]
    args.base_version = state["base_version"]
    args.lgrp = state["lgrp"]
    args.cust_version_number = state["cust_version_number"]
    args.preload_version_number = state["preload_version_number"]
    args.patch_version = state["patch_version"]
    if args.fingerprint and old_base and old_base != args.base_version and old_base in args.fingerprint:
        args.fingerprint = args.fingerprint.replace(old_base, args.base_version, 1)


def print_json(obj: Any) -> None:
    json.dump(obj, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def write_private(path: str, data: bytes) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRUSR | stat.S_IWUSR)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


def version_mentioned(text: str, needle: str) -> bool:
    if not needle:
        return False
    if needle.startswith("patch"):
        return needle in text
    return re.search(rf"(?<![\d.]){re.escape(needle)}(?![\d.])", text) is not None


def check_item_text(item: dict[str, Any]) -> str:
    info = item.get("blVersionInfo") if isinstance(item.get("blVersionInfo"), dict) else {}
    parts = [
        info.get("targetBlVersionNumber"),
        info.get("currentBlVersionNumber"),
        item.get("target"),
        item.get("current"),
    ]
    for comp in (item.get("targetBlComponents") or item.get("components") or []):
        if isinstance(comp, dict):
            parts.append(comp.get("versionNumber"))
            parts.append(comp.get("displayVersionNumber"))
    return " ".join(str(part) for part in parts if part)


def narrow_check(resp: dict[str, Any], target: str) -> dict[str, Any] | None:
    result = resp.get("result")
    if not isinstance(result, dict):
        return None
    kept = []
    for item in result.get("blVersionCheckResults") or []:
        if not isinstance(item, dict) or not version_mentioned(check_item_text(item), target):
            continue
        if not target.startswith("patch") and item.get("blVersionType") not in (1, None):
            continue
        kept.append(item)
    if not kept:
        return None
    narrowed = json.loads(json.dumps(resp))
    narrowed["result"]["blVersionCheckResults"] = kept
    return narrowed


def check_for_target(report: dict[str, Any], target: str) -> dict[str, Any]:
    if not target:
        return report.get("check") or {}
    sources = [report.get("check") or {}]
    sources.extend(step.get("check") or {} for step in report.get("walk") or [])
    for source in sources:
        narrowed = narrow_check(source, target)
        if narrowed is not None:
            return narrowed
    raise RuntimeError(
        f"no check hop offers {target}. The server only returns the next hop "
        "from the installed versions, then from each previous target."
    )


def bl_versions_from_check(
    resp: dict[str, Any], only_ids: list[str]
) -> tuple[list[dict[str, Any]], list[str]]:
    result = resp.get("result") if isinstance(resp.get("result"), dict) else resp
    items = result.get("blVersionCheckResults") or []
    wanted = [x for x in only_ids if x]
    versions: list[dict[str, Any]] = []
    ids: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        info = item.get("blVersionInfo") if isinstance(item.get("blVersionInfo"), dict) else {}
        packages = item.get("updatePackages") or []
        kept: list[dict[str, Any]] = []
        for pkg in packages:
            if not isinstance(pkg, dict):
                continue
            vid = str(pkg.get("versionId") or "")
            if not vid or (wanted and vid not in wanted):
                continue
            entry = {k: pkg[k] for k in PKG_KEYS if k in pkg}
            entry["versionId"] = vid
            kept.append(entry)
            if vid not in ids:
                ids.append(vid)
        if wanted and not kept:
            continue
        if not info and not kept:
            continue
        block: dict[str, Any] = {}
        if info:
            block["blVersionInfo"] = {k: info[k] for k in BL_INFO_KEYS if k in info}
        if kept:
            block["updatePackages"] = kept
        versions.append(block)
    for vid in wanted:
        if vid not in ids:
            ids.append(vid)
    return versions, ids


def build_authorize_body(
    args: argparse.Namespace,
    auth_params: dict[str, str],
    version_ids: list[str],
    bl_versions: list[dict[str, Any]],
) -> dict[str, Any]:
    if args.udid:
        info_id = args.udid
        ver = "2"
    else:
        info_id = args.imei or args.device_id
        ver = "1"
    body: dict[str, Any] = {
        "deviceInfo": {"deviceId": info_id},
        "deviceToken": auth_params["deviceId"],
        "updateToken": auth_params["updateToken"],
        "versionIdList": version_ids,
        "ver": ver,
    }
    if bl_versions:
        body["blVersions"] = bl_versions
    if args.key_attestation:
        body["keyAttestation"] = PathText(args.key_attestation)
    if args.device_certificate:
        body["deviceCertificate"] = PathText(args.device_certificate)
    return body


def decode_auth_payload(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("data="):
        chunk = text.split("&", 1)[0][5:]
        decoded = base64.b64decode(chunk)
        parsed = json.loads(decoded.decode("utf-8"))
        return parsed if isinstance(parsed, dict) else {"_value": parsed}
    parsed = json.loads(text or "{}")
    return parsed if isinstance(parsed, dict) else {"_value": parsed}


def find_d8() -> str | None:
    roots = [
        os.environ.get("ANDROID_SDK_ROOT", ""),
        os.environ.get("ANDROID_HOME", ""),
        "/opt/android/sdk",
    ]
    for root in roots:
        tools = os.path.join(root, "build-tools")
        if not os.path.isdir(tools):
            continue
        versions = sorted(os.listdir(tools), reverse=True)
        for version in versions:
            path = os.path.join(tools, version, "d8")
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
    return None


def ensure_auth_dex() -> str:
    dex_path = os.path.join(SCRIPT_DIR, "hnouc_auth.dex")
    java_mtime = os.path.getmtime(AUTH_JAVA)
    if os.path.isfile(dex_path) and os.path.getmtime(dex_path) >= java_mtime:
        return dex_path
    d8 = find_d8()
    if not d8:
        raise RuntimeError("d8 not found under ANDROID_SDK_ROOT or /opt/android/sdk/build-tools")
    work = os.path.join(SCRIPT_DIR, ".hnouc_auth_build")
    os.makedirs(work, exist_ok=True)
    javac = subprocess.run(
        ["javac", "--release", "8", "-d", work, AUTH_JAVA],
        capture_output=True,
        text=True,
    )
    if javac.returncode != 0:
        raise RuntimeError(javac.stderr.strip() or "javac failed")
    class_file = os.path.join(work, "HnOucAuth.class")
    packed = subprocess.run(
        [d8, "--output", work, class_file],
        capture_output=True,
        text=True,
    )
    if packed.returncode != 0:
        raise RuntimeError(packed.stderr.strip() or "d8 failed")
    built = os.path.join(work, "classes.dex")
    os.replace(built, dex_path)
    return dex_path


def adb_push(local: str, remote: str) -> None:
    r = subprocess.run(["adb", "push", local, remote], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip() or f"adb push {remote} failed")


def phone_auth_main(dex_remote: str, *args: str) -> str:
    quoted = " ".join("'" + a.replace("'", "'\\''") + "'" for a in args)
    command = (
        f"CLASSPATH={dex_remote} app_process /system/bin HnOucAuth {quoted}"
    )
    return adb_shell(command, root=True, timeout=60)


def parse_phone_json(text: str) -> dict[str, Any]:
    start = text.find("JSON ")
    if start < 0:
        raise RuntimeError(f"phone did not return auth params: {text.strip()[:400]}")
    parsed, _ = json.JSONDecoder().raw_decode(text[start + 5:].lstrip())
    if not isinstance(parsed, dict):
        raise RuntimeError("getUpdateAuthParams did not return a JSON object")
    return parsed


def load_auth_params(args: argparse.Namespace) -> dict[str, str]:
    if args.pull_auth_params:
        dex = ensure_auth_dex()
        adb_push(dex, PHONE_DEX)
        text = phone_auth_main(PHONE_DEX, "dump")
        parsed = parse_phone_json(text)
        missing = [k for k in ("deviceId", "updateToken", "TokenHmac") if not parsed.get(k)]
        if missing:
            raise RuntimeError(f"getUpdateAuthParams missing {', '.join(missing)}")
        if args.auth_params:
            write_private(
                args.auth_params,
                json.dumps(
                    {k: parsed[k] for k in ("deviceId", "updateToken", "TokenHmac")},
                    separators=(",", ":"),
                ).encode(),
            )
        return {k: str(parsed[k]) for k in ("deviceId", "updateToken", "TokenHmac")}
    if not args.auth_params:
        raise RuntimeError("authorize needs --auth-params or --pull-auth-params")
    with open(args.auth_params, "r", encoding="utf-8") as f:
        parsed = json.load(f)
    missing = [k for k in ("deviceId", "updateToken", "TokenHmac") if not parsed.get(k)]
    if missing:
        raise RuntimeError(f"{args.auth_params} missing {', '.join(missing)}")
    return {k: str(parsed[k]) for k in ("deviceId", "updateToken", "TokenHmac")}


def cmd_authorize(args: argparse.Namespace, check_resp: dict[str, Any]) -> dict[str, Any]:
    only_ids = [x.strip() for x in (args.auth_version_ids or "").split(",") if x.strip()]
    bl_versions, version_ids = bl_versions_from_check(check_resp, only_ids)
    if not version_ids:
        raise RuntimeError(
            "check response has no updatePackages versionId; "
            "pass --auth-version-ids or a --check-file from a hop that offers packages"
        )
    auth_params = load_auth_params(args)
    body = build_authorize_body(args, auth_params, version_ids, bl_versions)
    out_dir = args.auth_out or os.path.join(SCRIPT_DIR, "auth_out")
    os.makedirs(out_dir, exist_ok=True)
    request_path = os.path.join(out_dir, "authorize_request.json")
    write_private(request_path, json.dumps(body, separators=(",", ":")).encode())
    status, raw = curl(
        AUTHORIZE_URL,
        method="POST",
        headers=check_headers(args),
        data=json.dumps(body, separators=(",", ":")).encode(),
        proxy=args.proxy,
        timeout=args.timeout,
        user_agent=args.check_user_agent,
    )
    response_path = os.path.join(out_dir, "authorize_response.txt")
    write_private(response_path, raw)
    sa_path = os.path.join(out_dir, "update_auth.sa")
    if status == 200 and raw:
        write_private(sa_path, raw)
    report: dict[str, Any] = {
        "authorizeHttp": status,
        "authorizeUrl": AUTHORIZE_URL,
        "versionIds": version_ids,
        "requestFile": request_path,
        "responseFile": response_path,
    }
    if status == 200 and raw:
        report["updateAuthSa"] = sa_path
    text = raw.decode("utf-8", "replace")
    try:
        payload = decode_auth_payload(text)
    except (json.JSONDecodeError, ValueError, binascii.Error):
        payload = {}
        report["decodeError"] = True
    approved = []
    for item in payload.get("approvedVersionList") or []:
        if isinstance(item, dict):
            status_value = item.get("status")
            approved.append(
                {
                    "versionId": str(item.get("versionId") or ""),
                    "status": "" if status_value is None else str(status_value),
                }
            )
    if approved:
        report["approvedVersionList"] = approved
    if payload.get("updateToken"):
        report["updateTokenMatch"] = payload.get("updateToken") == auth_params["updateToken"]
    return report


def cmd_check(args: argparse.Namespace) -> int:
    if args.from_adb:
        apply_from_adb(args)
    if not args.filelist_ids_only and not args.check_file:
        missing = [n for n in ("model", "cust", "device_id", "base_version") if not getattr(args, n)]
        if missing:
            print(
                f"missing required params: {', '.join(missing)} (pass flags or --from-adb)",
                file=sys.stderr,
            )
            return 2

    report: dict[str, Any] = {
        "device": {
            "model": args.model,
            "cust": args.cust,
            "vendorCountry": args.vendor_country or f"{args.country}_{args.vendor}",
            "boardID": args.board_id,
            "deviceId": args.device_id,
            "fingerprint": args.fingerprint,
            "clientVersion": args.client_version,
            "base": getattr(args, "base_version_number", "") or f"{args.lgrp} {args.base_version}".strip(),
            "custPkg": getattr(args, "cust_version_number", "")
            or f"{args.model}-CUST {args.cust_version}({args.cust})",
            "preloadPkg": getattr(args, "preload_version_number", "")
            or f"{args.model}-PRELOAD {args.preload_version}({args.cust}R2)",
        },
        "hops": [],
        "packages": [],
        "filelists": [],
    }

    if args.check_file:
        with open(args.check_file, "r", encoding="utf-8") as f:
            saved = json.load(f)
        report["checkHttp"] = saved.get("checkHttp", 200) if "check" in saved else 200
        report["check"] = saved.get("check", saved)
    elif not args.filelist_ids_only:
        body = build_check_body(args)
        if args.dump_request:
            print_json({"url": CHECK_URL, "headers": check_headers(args), "body": body})
        http, resp = version_check(args, body)
        report["checkHttp"] = http
        report["check"] = resp
        hops, version_list = summarize_check(resp)
        report["hops"] = hops
        if http == 401:
            report["note"] = (
                "HTTP 401 / 101003731: server wants HnPKI (keyAttestation + "
                "deviceCertificate). Logcat strips those fields. Pass "
                "--key-attestation / --device-certificate if you extract them "
                "from OEMINFO KEY_ATTESTATION / DEVICE_CERTIFICATE1."
            )
        ids = []
        description_ids = set()
        for v in version_list:
            vid = str(v.get("versionId") or "")
            number = str(v.get("versionNumber") or "")
            if vid:
                ids.append(vid)
            if vid and number.isdigit():
                description_ids.add(vid)
            report["packages"].append(
                {
                    "versionId": vid,
                    "versionNumber": v.get("versionNumber"),
                    "url": v.get("url") or cdn_url(vid, "full/"),
                }
            )
        for hop in hops:
            for pkg in hop.get("updatePackages") or []:
                vid = str(pkg.get("versionId") or "")
                if vid and vid not in ids:
                    ids.append(vid)
            desc = str(hop.get("descriptPackageId") or "")
            if desc:
                description_ids.add(desc)
                if desc not in ids:
                    ids.append(desc)
        if args.filelist:
            for vid in ids:
                if vid in description_ids:
                    continue
                report["filelists"].append(fetch_filelist(args, vid))

        target_already_offered = bool(args.auth_target) and narrow_check(resp, args.auth_target) is not None
        if (args.walk or (args.auth_target and not target_already_offered)) and hops:
            seen = {installed_key(args)}
            frontier = hops
            while frontier and len(report.setdefault("walk", [])) < 8:
                advanced = False
                for hop in frontier:
                    state = full_hop_state(args, hop)
                    if state is None:
                        continue
                    key = (
                        state["base_version_number"],
                        state["cust_version_number"],
                        state["preload_version_number"],
                        state["patch_version"],
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    apply_installed(args, state)
                    body = build_check_body(args)
                    http, resp = version_check(args, body)
                    more_hops, more_vers = summarize_check(resp)
                    report["walk"].append(
                        {
                            "from": {
                                "base": state["base_version_number"],
                                "cust": state["cust_version_number"],
                                "preload": state["preload_version_number"],
                                "patch": state["patch_version"],
                            },
                            "http": http,
                            "errCode": resp.get("errCode"),
                            "hops": more_hops,
                            "check": resp,
                        }
                    )
                    if args.filelist:
                        have = {f.get("versionId") for f in report["filelists"]}
                        for v in more_vers:
                            vid = str(v.get("versionId") or "")
                            number = str(v.get("versionNumber") or "")
                            if not vid or vid in have or number.isdigit():
                                continue
                            report["filelists"].append(fetch_filelist(args, vid))
                            have.add(vid)
                    if http != 200 or resp.get("status") not in (0, "0", None):
                        frontier = []
                    elif args.auth_target and not args.walk and narrow_check(resp, args.auth_target):
                        frontier = []
                    else:
                        frontier = more_hops
                    advanced = True
                    break
                if not advanced:
                    break

    extra_ids = [x.strip() for x in (args.filelist_ids or "").split(",") if x.strip()]
    if extra_ids:
        have = {f.get("versionId") for f in report["filelists"]}
        for vid in extra_ids:
            if vid not in have:
                report["filelists"].append(fetch_filelist(args, vid))

    print_json(report)
    if not args.authorize:
        return 0 if report.get("checkHttp", 200) in (200, None) else 1
    if report.get("checkHttp", 200) not in (200, None):
        print("authorize skipped: version/check did not return HTTP 200", file=sys.stderr)
        return 1
    try:
        auth_report = cmd_authorize(args, check_for_target(report, args.auth_target))
    except (RuntimeError, json.JSONDecodeError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"authorize failed: {exc}", file=sys.stderr)
        return 1
    print_json(auth_report)
    approved = auth_report.get("approvedVersionList") or []
    approved_ok = bool(approved) and all(item.get("status") == "0" for item in approved)
    return 0 if auth_report.get("authorizeHttp") == 200 and auth_report.get("updateTokenMatch") is True and approved_ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--proxy", default=DEFAULT_PROXY, help="curl --proxy value (default: %(default)s)")
    p.add_argument("--user-agent", default=DEFAULT_UA, help="UA for CDN GETs")
    p.add_argument("--check-user-agent", default="", help="UA for version/check (phone sends none)")
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--from-adb", action="store_true", help="fill model/cust/versions/serial from adb getprop")
    p.add_argument("--model", default="")
    p.add_argument("--cust", default="", help="C-version, e.g. C636")
    p.add_argument("--vendor", default="")
    p.add_argument("--country", default="")
    p.add_argument("--vendor-country", default="", help="commonRules.vendorCountry; --from-adb reads /data/custom.bin")
    p.add_argument("--device-id", default="", help="serial; used as deviceInfo.deviceId when udid/imei are empty")
    p.add_argument("--udid", default="", help="when set, authorize ver=2 and deviceInfo.deviceId is the udid")
    p.add_argument("--imei", default="", help="deviceInfo.deviceId when udid is empty")
    p.add_argument("--fingerprint", default="", help="commonRules.fingerPrint; --from-adb reads ro.build.fingerprint")
    p.add_argument("--c-version", default="", help="commonRules.cVersion; defaults to --cust")
    p.add_argument("--board-id", default="8119")
    p.add_argument("--lgrp", default="")
    p.add_argument("--base-version", default="")
    p.add_argument("--base-version-number", default="", help="type 2 versionNumber; --from-adb uses the raw property")
    p.add_argument("--cust-version", default="")
    p.add_argument("--cust-version-number", default="", help="type 3 versionNumber; --from-adb uses the raw property")
    p.add_argument("--preload-version", default="")
    p.add_argument("--preload-version-number", default="", help="type 4 versionNumber; --from-adb uses the raw property")
    p.add_argument("--patch-version", default="patch00", help="wire type 13; V5 sends patch00 when /patch_hn/patch.prop is absent")
    p.add_argument("--cota-version", default="")
    p.add_argument("--platform-version", default="")
    p.add_argument("--software-platform", default="")
    p.add_argument("--gms-version", default="")
    p.add_argument("--os", default="")
    p.add_argument("--language", default="en-us")
    p.add_argument("--d-version", default="D000")
    p.add_argument("--client-version", default="140100136")
    p.add_argument("--client-name", default="14.1.0.136")
    p.add_argument("--ram", default="17 GB")
    p.add_argument("--emmc", default="512 GB")
    p.add_argument("--cpu", default="8_3.2GHz")
    p.add_argument("--action", default="upgrade", choices=["upgrade", "recovery", "patchCheck", "cotaInitial", "logOnly"])
    p.add_argument("--check-mode", default="NORMAL")
    p.add_argument("--log-only", action="store_true")
    p.add_argument("--key-attestation", default="", help="file with HnPKI keyAttestation blob")
    p.add_argument("--device-certificate", default="", help="file with HnPKI deviceCertificate blob")
    p.add_argument("--filelist", action="store_true", help="GET filelist.xml for ids from the check response")
    p.add_argument("--filelist-ids", default="", help="comma-separated versionIds to fetch from CDN")
    p.add_argument("--filelist-ids-only", action="store_true", help="skip version/check, only fetch --filelist-ids")
    p.add_argument("--walk", action="store_true", help="re-check using each target as the new current base")
    p.add_argument("--dump-request", action="store_true")
    p.add_argument("--check-file", default="", help="saved version/check JSON, or a previous script report")
    p.add_argument("--authorize", action="store_true", help="POST /blversion/v1/version/authorize for the check hop")
    p.add_argument("--auth-target", default="", help="OTA version to authorize, e.g. 10.0.0.122 or patch01")
    p.add_argument("--auth-params", default="", help="JSON with deviceId, updateToken, TokenHmac from the phone")
    p.add_argument("--pull-auth-params", action="store_true", help="call HnOucNative.getUpdateAuthParams on the phone")
    p.add_argument("--auth-version-ids", default="", help="comma-separated versionIds; default is every id in the check hop")
    p.add_argument("--auth-out", default="", help="directory for the request, raw response, and update_auth.sa")
    p.set_defaults(func=cmd_check)
    return p


def main() -> int:
    args = build_parser().parse_args()
    if not args.check_user_agent:
        args.check_user_agent = None
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

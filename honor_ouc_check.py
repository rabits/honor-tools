#!/usr/bin/env python3
"""Honor HnOUC baseline-version check client (MagicOS 8 / HnOUC 14.1.0.136).

Reconstructed from HnOUC.apk + logcat_OUC.log (VER-N49 / C636):

  POST https://update.platform.hihonorcloud.com/blversion/v1/version/check
  headers: x-productId, x-deviceDescId, x-devModel, x-requestId
           Content-Type: application/json; charset=UTF-8
           Accept-Encoding: identity
  body:    commonRules + versionPackageRules + deviceInfo
           (+ optional keyAttestation / deviceCertificate — stripped from logcat)

  CDN:     http://update.hihonorcdn.com/TDS/data/bl/files/v{id}/f1/full/filelist.xml
           http://update.hihonorcdn.com/TDS/data/bl/files/v{id}/f1/{file}

update.hihonorcdn.com is WAF-gated (HTTP 567 / 514 / 403 from this network).
Use the SOCKS5 proxy + Firefox UA that already works:

  --proxy socks5://127.0.0.1:1080
  --user-agent 'Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/144.0'

The check API returns the *next* hop for the current component versions, not a
full catalog. --walk follows that chain. A live current version that has an
update typically requires HnPKI (keyAttestation + deviceCertificate from
ProtectAreaEx / OEMINFO); without it the server answers HTTP 401 / 101003731.

Examples:
  python3 tools/honor_ouc_check.py --from-adb
  python3 tools/honor_ouc_check.py --from-adb --walk --filelist
  python3 tools/honor_ouc_check.py --filelist-ids 474462,335329,335330
  python3 tools/honor_ouc_check.py --model VER-N49 --cust C636 --base-version 8.0.0.105

  # After dumping HnPKI with zygote-CVE-2024-31317 --dump-pki:
  python3 tools/honor_ouc_check.py --from-adb \
    --key-attestation pki/key_attestation.txt \
    --device-certificate pki/device_certificate.txt --walk --filelist
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
from typing import Any

DEFAULT_PROXY = "socks5://127.0.0.1:1080"
DEFAULT_UA = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/144.0"
)
CHECK_URL = "https://update.platform.hihonorcloud.com/blversion/v1/version/check"
CDN_HOST = "http://update.hihonorcdn.com"
CDN_PREFIX = "/TDS/data/bl/files"

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


def build_check_body(args: argparse.Namespace) -> dict[str, Any]:
    incremental = f"{args.base_version}{args.cust}E2R2P2"
    rules: list[dict[str, Any]] = [
        {"versionPackageType": 2, "versionNumber": f"{args.lgrp} {args.base_version}"},
        {"versionPackageType": 3, "versionNumber": f"{args.model}-CUST {args.cust_version}({args.cust})"},
        {"versionPackageType": 4, "versionNumber": f"{args.model}-PRELOAD {args.preload_version}({args.cust}R2)"},
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
            "devModel": args.model,
            "fingerPrint": fingerprint(args.model, incremental),
            "language": args.language,
            "os": args.os,
            "subGroup": "",
            "verGroup": "",
            "vnKey": ";",
            "saleInfo": sale_info(
                args.vendor, args.country, args.software_platform,
                args.ram, args.emmc, args.cpu, args.client_name,
            ),
            "vendorCountry": f"{args.country}_{args.vendor}",
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


def apply_from_adb(args: argparse.Namespace) -> None:
    args.model = args.model or adb_getprop("ro.product.model")
    args.cust = args.cust or adb_getprop("ro.product.CustCVersion")
    args.device_id = args.device_id or adb_getprop("ro.serialno")
    args.board_id = args.board_id or adb_getprop("ro.board.boardid")
    base = adb_getprop("ro.comp.hl.product_base_version")
    if base and " " in base:
        lgrp, ver = base.rsplit(" ", 1)
        args.lgrp = args.lgrp or lgrp
        args.base_version = args.base_version or ver
    custv = adb_getprop("ro.comp.hl.product_cust_version")
    # VER-N49-CUST 8.0.0.2(C636)
    if custv and "(" in custv:
        left, _ = custv.split("(", 1)
        args.cust_version = args.cust_version or left.rsplit(" ", 1)[-1]
    pre = adb_getprop("ro.comp.hl.product_preload_version")
    if pre and "(" in pre:
        left, _ = pre.split("(", 1)
        args.preload_version = args.preload_version or left.rsplit(" ", 1)[-1]
    plat = adb_getprop("ro.build.version.magic")
    if plat:
        args.software_platform = args.software_platform or plat
        if plat.startswith("MagicOS_"):
            args.platform_version = args.platform_version or plat.split("_", 1)[1]
    args.gms_version = args.gms_version or adb_getprop("ro.com.google.gmsversion")
    vendorcountry = adb_getprop("ro.boot.vendorcountry") or adb_getprop("ro.product.VendorCountry")
    if "/" in vendorcountry:
        country, vendor = vendorcountry.split("/", 1)
        args.country = args.country or country
        args.vendor = args.vendor or vendor
    args.os = args.os or f"Android {adb_getprop('ro.build.version.release')}"


def print_json(obj: Any) -> None:
    json.dump(obj, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def cmd_check(args: argparse.Namespace) -> int:
    if args.from_adb:
        apply_from_adb(args)
    if not args.filelist_ids_only:
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
            "vendorCountry": f"{args.country}_{args.vendor}",
            "deviceId": args.device_id,
            "base": f"{args.lgrp} {args.base_version}",
            "custPkg": f"{args.model}-CUST {args.cust_version}({args.cust})",
            "preloadPkg": f"{args.model}-PRELOAD {args.preload_version}({args.cust}R2)",
        },
        "hops": [],
        "packages": [],
        "filelists": [],
    }

    if not args.filelist_ids_only:
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
        for v in version_list:
            vid = str(v.get("versionId") or "")
            if vid:
                ids.append(vid)
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
            desc = hop.get("descriptPackageId")
            if desc and str(desc) not in ids:
                ids.append(str(desc))
        if args.filelist:
            for vid in ids:
                report["filelists"].append(fetch_filelist(args, vid))

        if args.walk and hops:
            current = args.base_version
            seen = {current}
            for hop in hops:
                target = hop.get("target") or ""
                # VER-N49 8.0.0.142(C636E2R2P2) → 8.0.0.142
                num = None
                if target:
                    parts = target.replace("(", " ").split()
                    for p in parts:
                        if p.count(".") >= 2:
                            num = p
                            break
                if not num or num in seen:
                    continue
                seen.add(num)
                args.base_version = num
                body = build_check_body(args)
                http, resp = version_check(args, body)
                more_hops, more_vers = summarize_check(resp)
                report.setdefault("walk", []).append({"from": num, "http": http, "hops": more_hops, "check": resp})
                if http != 200:
                    break

    extra_ids = [x.strip() for x in (args.filelist_ids or "").split(",") if x.strip()]
    if extra_ids:
        have = {f.get("versionId") for f in report["filelists"]}
        for vid in extra_ids:
            if vid not in have:
                report["filelists"].append(fetch_filelist(args, vid))

    print_json(report)
    return 0 if report.get("checkHttp", 200) in (200, None) else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--proxy", default=DEFAULT_PROXY, help="curl --proxy value (default: %(default)s)")
    p.add_argument("--no-proxy", action="store_true")
    p.add_argument("--user-agent", default=DEFAULT_UA, help="UA for CDN GETs")
    p.add_argument("--check-user-agent", default="", help="UA for version/check (phone sends none)")
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--from-adb", action="store_true", help="fill model/cust/versions/serial from adb getprop")
    p.add_argument("--model", default="")
    p.add_argument("--cust", default="", help="C-version, e.g. C636")
    p.add_argument("--vendor", default="spcseas")
    p.add_argument("--country", default="def")
    p.add_argument("--device-id", default="", help="x-deviceDescId / deviceInfo.deviceId (SN)")
    p.add_argument("--udid", default="")
    p.add_argument("--board-id", default="8119")
    p.add_argument("--lgrp", default="VER-LGRP2-OVS")
    p.add_argument("--base-version", default="")
    p.add_argument("--cust-version", default="8.0.0.2")
    p.add_argument("--preload-version", default="8.0.0.2")
    p.add_argument("--patch-version", default="patch02")
    p.add_argument("--cota-version", default="cota8.0.0")
    p.add_argument("--platform-version", default="8.0.0")
    p.add_argument("--software-platform", default="MagicOS_8.0.0")
    p.add_argument("--gms-version", default="14_202401")
    p.add_argument("--os", default="Android 14")
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
    p.set_defaults(func=cmd_check)
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.no_proxy:
        args.proxy = ""
    if not args.check_user_agent:
        args.check_user_agent = None
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

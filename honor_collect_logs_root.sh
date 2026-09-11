#!/usr/bin/env bash
# Collect current-boot XBL/ABL logs (and whatever kernel log is still in the ringbuffer).
# Usage: ./honor_collect_logs_root.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
ADB="${ADB:-adb}"
HOST_STAGING="$(mktemp -d "${TMPDIR:-/tmp}/bootlogs.XXXXXX")"
REMOTE_WORK="/data/local/tmp/honor_collect_logs_root"
REMOTE_SH="${REMOTE_WORK}/collect.sh"

cleanup() {
  rm -rf "${HOST_STAGING}"
}
trap cleanup EXIT

if ! "${ADB}" get-state >/dev/null 2>&1; then
  echo "adb device is not online" >&2
  exit 1
fi

HIMNTN_PY="${ROOT}/himntn_rawdump_root.py"
if [ -f "${HIMNTN_PY}" ]; then
  echo "---- HIMNTN / log_buf_len pre-check ----" >&2
  if ! python3 "${HIMNTN_PY}" --adb "${ADB}" --check-collect; then
    echo "himntn_rawdump_root.py pre-check failed (continuing collect)" >&2
  fi
  echo "----------------------------------------" >&2
  echo >&2
fi

cat > "${HOST_STAGING}/collect.sh" << 'REMOTE'
#!/system/bin/sh
set -e

WORK="/data/local/tmp/honor_collect_logs_root"
OUT="$WORK/out"
LOGFS="$WORK/logfs_mnt"
rm -rf "$OUT"
mkdir -p "$WORK/logfs" "$WORK/rawdump_last_ramdump" "$LOGFS" "$OUT"

mount -t vfat -o ro /dev/block/by-name/logfs "$LOGFS" 2>/dev/null || true
if ! grep -q " $LOGFS " /proc/mounts; then
  echo "failed to mount logfs" >&2
  exit 1
fi

# Latest ABL wall-clock boot (Honor RTC). Android userspace clock can drift.
# UefiLog files are CRLF; strip CR before parsing.
BOOTTIME_LINE="$(grep -ah '^boottime: 20' "$LOGFS"/UefiLog*.txt 2>/dev/null | tr -d '\r' | sort | tail -n 1 || true)"
if [ -n "$BOOTTIME_LINE" ]; then
  BOOT_STAMP="$(printf '%s\n' "$BOOTTIME_LINE" | awk '{
    gsub(/[-:]/, "", $2)
    gsub(/[-:]/, "", $3)
    printf "%s%s", $2, $3
  }')"
else
  NOW="$(date +%s)"
  UP="$(awk '{print int($1)}' /proc/uptime)"
  BOOT_EPOCH=$((NOW - UP))
  BOOT_STAMP="$(date -d "@$BOOT_EPOCH" +%Y%m%d%H%M%S 2>/dev/null || date +%Y%m%d%H%M%S)"
fi

# xmntn suffix is CLOCK_MONOTONIC tv_nsec/10. uptime's fractional second is that field.
TICK="$(awk '{
  split($1, a, ".")
  frac = (a[2] ? a[2] : "0") "000000000"
  printf "%08d", int(substr(frac, 1, 9) / 10)
}' /proc/uptime)"

NAME="${BOOT_STAMP}-${TICK}"
DEST="$OUT/$NAME"
mkdir -p "$DEST/logfs" "$DEST/rawdump_last_ramdump"

cp -a "$LOGFS"/UefiLog*.txt "$DEST/logfs/" 2>/dev/null || true
cp -a "$LOGFS"/FlagTime.txt "$DEST/logfs/" 2>/dev/null || true

CURRENT_XBL="$DEST/xbl_abl"
: > "$CURRENT_XBL"
if [ -n "$BOOTTIME_LINE" ]; then
  BT="$(printf '%s\n' "$BOOTTIME_LINE" | sed 's/^boottime: //')"
  for f in $(ls "$LOGFS"/UefiLog*.txt | sort); do
    if tr -d '\r' < "$f" | grep -q "boottime: ${BT}"; then
      tr -d '\000\r' < "$f" >> "$CURRENT_XBL"
    fi
  done
fi
if [ ! -s "$CURRENT_XBL" ]; then
  NEWEST="$(ls -1t "$LOGFS"/UefiLog*.txt | head -n 1)"
  tr -d '\000\r' < "$NEWEST" > "$CURRENT_XBL"
fi

dd if=/dev/block/by-name/xbl_sc_logs of="$DEST/xbl_sc_logs" bs=4096 2>/dev/null || true
cat /proc/pmic_pon_log > "$DEST/pmic_pon_log" 2>/dev/null || true
cat /proc/cmdline > "$DEST/cmdline" 2>/dev/null || true
cat /proc/sys/kernel/random/boot_id > "$DEST/boot_id" 2>/dev/null || true

dmesg > "$DEST/kmsg" 2>/dev/null || true
timeout 2 cat /proc/vmkmsg > "$DEST/vmkmsg" 2>/dev/null || true
/system/bin/logcat -b kernel -d > "$DEST/logcat_kernel" 2>/dev/null || true
ls /sys/fs/pstore > "$DEST/pstore_list" 2>/dev/null || true
for p in /sys/fs/pstore/*; do
  [ -f "$p" ] || continue
  cat "$p" > "$DEST/pstore_$(basename "$p")" 2>/dev/null || true
done

dd if=/dev/block/by-name/rawdump of="$DEST/rawdump_last_ramdump/xbl_abl" bs=4096 skip=128 count=64 2>/dev/null || true
dd if=/dev/block/by-name/rawdump of="$DEST/rawdump_last_ramdump/last_xbl_abl" bs=4096 skip=192 count=64 2>/dev/null || true
dd if=/dev/block/by-name/rawdump of="$DEST/rawdump_last_ramdump/last_kmsg" bs=4096 skip=512 count=384 2>/dev/null || true
dd if=/dev/block/by-name/rawdump of="$DEST/rawdump_last_ramdump/tz_log" bs=4096 skip=768 count=256 2>/dev/null || true
for f in "$DEST/rawdump_last_ramdump"/*; do
  [ -f "$f" ] || continue
  tr -d '\000' < "$f" > "$f.txt"
  mv "$f.txt" "$f"
done

KMSG_FIRST="$(sed -n '1p' "$DEST/kmsg" 2>/dev/null || true)"
{
  echo "name=$NAME"
  echo "abl_boottime=${BOOTTIME_LINE:-unknown}"
  echo "android_now=$(date)"
  echo "uptime=$(cat /proc/uptime)"
  echo "boot_id=$(cat /proc/sys/kernel/random/boot_id 2>/dev/null)"
  echo "cmdline_log_buf=$(tr ' ' '\n' < /proc/cmdline | grep log_buf_len || true)"
  echo "kmsg_first_line=$KMSG_FIRST"
  echo
  echo "xbl_abl is concatenated UefiLog*.txt for the latest ABL boottime (current boot XBL+ABL)."
  echo "Kernel printk size is the last log_buf_len= on cmdline (DTB 1M unless HIMNTN log_buf_len_4m appended 4M)."
  echo "After a long uptime with 1M the ring wraps and early kmsg is gone from dmesg."
  echo "rawdump_last_ramdump/ is the previous XBL ramdump (last panic), not this boot."
  echo "To catch early kernel of THIS boot: enable HIMNTN log_buf_len_4m (./himntn_rawdump.py --enable log_buf_len_4m), reboot, collect soon after."
} > "$DEST/META.txt"

umount "$LOGFS" 2>/dev/null || true
rmdir "$LOGFS" 2>/dev/null || true
printf '%s\n' "$NAME"
REMOTE

echo "Pushing collector..." >&2
"${ADB}" exec-out su -c "mkdir -p ${REMOTE_WORK}" >/dev/null
"${ADB}" push "${HOST_STAGING}/collect.sh" /data/local/tmp/honor_collect_logs_root.sh >/dev/null
"${ADB}" exec-out su -c "mv /data/local/tmp/honor_collect_logs_root.sh ${REMOTE_SH} && chmod 755 ${REMOTE_SH}" >/dev/null

echo "Collecting on device..." >&2
NAME="$("${ADB}" exec-out su -c "sh ${REMOTE_SH}" | tr -d '\r' | tail -n 1)"
if [ -z "${NAME}" ] || ! printf '%s' "${NAME}" | grep -qE '^[0-9]{14}-[0-9]{8}$'; then
  echo "failed to compute dump folder name: '${NAME}'" >&2
  exit 1
fi

echo "Pulling ${NAME}..." >&2
"${ADB}" exec-out su -c "tar -C ${REMOTE_WORK}/out -cf - ${NAME}" > "${HOST_STAGING}/bootlogs.tar"
mkdir -p "${ROOT}/bootlogs"
if ! tar -tf "${HOST_STAGING}/bootlogs.tar" >/dev/null 2>&1; then
  echo "tar stream failed, falling back to adb pull" >&2
  "${ADB}" exec-out su -c "chmod -R a+rX ${REMOTE_WORK}/out/${NAME}"
  "${ADB}" pull "${REMOTE_WORK}/out/${NAME}" "${ROOT}/bootlogs/${NAME}" >/dev/null
else
  tar -C "${ROOT}/bootlogs" -xf "${HOST_STAGING}/bootlogs.tar"
fi
"${ADB}" exec-out su -c "rm -rf ${REMOTE_WORK} /data/local/tmp/honor_collect_logs_root.sh" >/dev/null 2>&1 || true

echo "Wrote ${ROOT}/bootlogs/${NAME}"
ls -la "${ROOT}/bootlogs/${NAME}"
echo
echo "---- META ----"
cat "${ROOT}/bootlogs/${NAME}/META.txt"

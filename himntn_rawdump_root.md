# himntn_rawdump.py

WARNING: Applicable to Honor Magic V5 9.0.1.160

Read-only helper for the Honor Magic V5 HIMNTN mask stored at the start of
`/dev/block/by-name/rawdump`. It never writes to the device. `--enable` /
`--disable` only print the resulting 8-byte value and a copy-paste `dd`
command.

Effects below are from ABL `HimntnAbl.c` in `abl.pe` (ROM 9.0.1.160) plus
userspace consumers in `UNPACKED_ROM_V5_9.0.1.160`. Unknown bits have no
ABL string on this device — do not flip them.

## Usage

```bash
./himntn_rawdump.py                              # adb + su, read rawdump
./himntn_rawdump.py --from 0x00fef6851c404948    # 8-byte memory dump
./himntn_rawdump.py --from 0x401C85F6FE00        # 48-bit mask from cmdline
./himntn_rawdump.py --enable log_buf_len_4m      # print dd, do not apply
./himntn_rawdump.py --disable uart_earlycon --enable printk_devkmsg
./himntn_rawdump.py --list
./himntn_rawdump.py --check-collect              # used by collect_current_boot_logs.sh
```

`--from` accepts:

| input | meaning |
|-------|---------|
| 16 hex digits ending in `4948` | little-endian 8 bytes as `xxd`/`od` prints them |
| `0x4849…` (HI magic in the high bits) | stored u64 |
| ≤ 48-bit integer | cmdline-style mask (`HIMNTN=0x401C85F6FE00`) |

The emitted `dd` does a 512-byte read-modify-write of offset 0 (HIMNTN is only
the first 8 bytes; bytes 8+ are rainbow/bootfail header). After a successful
write, **reboot** — ABL applies the mask before Android init.

`collect_current_boot_logs.sh` runs `--check-collect` first and recommends
`log_buf_len_4m` if the printk ring is still 1M.

## Storage

```
rawdump offset 0, 8 bytes LE
stored = (mask & 0xFFFFFFFFFFFF) | 0x4849000000000000   # ASCII "HI"
ABL recovers mask as stored & 0xB7B6FFFFFFFFFFFF
item n is on iff bit (47-n) of the mask is set
```

Example from this device (factory-like mask):

```
memory:  00 fe f6 85 1c 40 49 48
stored:  0x4849401C85F6FE00
mask:    0x401C85F6FE00
```

`fastboot oem himntn` talks the same 48-character `0`/`1` string (item 0 =
first char). On an unlocked user build the command is rejected with
`Command not allowed` — that is an ABL ACL, not a signature. There is no
HMAC/RSA on this blob.

## Who else touches rawdump

| actor | role |
|---|---|
| ABL | HIMNTN RMW; rainbow reason at +8; ABL log at `0x84000` |
| xmntn `-h 1` | on **non-commercial** builds may rewrite HIMNTN; commercial/user skips when `factory_marker` is on |
| xmntn `-r 1` | copies ramdump slices into `/data/vendor/log/reliability/dumplog/` (`xbl_abl` @ `0x80000`, `last_kmsg` @ `0x200000`, …) |
| recovery `factory_reset` | `DoDisableHimntn` on factory reset |
| `rainbow.ko` | `rb_header.himntn_data` in reserved RAM (`rainbow_mem@ff300000`) — RAM mirror, not NV |
| `qcom-dload-mode.ko` | `persist.vendor.sys.rawdump_copy` → eMMC ramdump payload; can clobber offset 0 |
| `xbl_ramdump` | reads board id from rawdump |
| hiview | uploads already-copied `dumplog/*/rawdump.bin` |

SELinux: explicit `blk_file` RW on `vendor_rawdump_block_device` is only
granted to `xmntn`. Root via KernelSU bypasses that.

---

## How a bit becomes a boot effect

```
rawdump[0:8]  --ABL-->  cmdline / bootconfig  --kernel-->  ro.boot.*
                                              --init.rc-->  services, sysfs, USB, SSR
```

Inverted items: the **named effect** is active when the HIMNTN **bit is 0**.
The script’s `--enable name` turns the *effect* on (and clears the bit if
inverted).

Current device (`HIMNTN=0x401C85F6FE00`, `ro.boot.labexternal=false`,
`log_buf_len=1M`) is noted under each item.

---

### `log_buf_len_4m` — item `0x1c` (28) — currently **off**

ABL appends ` log_buf_len=4M` after the DTB token `log_buf_len=1M`. The later
token wins: kernel allocates a 4MiB printk ring instead of 1MiB.

**On:** early kmsg survives much longer; `dmesg` after minutes of uptime still
reaches closer to time 0. This is the bit `collect_current_boot_logs.sh` wants.

**Off (now):** 1M ring wraps; after a long uptime dmesg starts mid-boot.

No Android property. Kernel-only. Low risk. Needs reboot.

---

### `printk_devkmsg` — item `0x1d` (29), **inverted** — effect currently **off**

When the **bit is 0**, ABL appends ` printk.devkmsg=on`. That is the kernel
parameter for `/dev/kmsg` (see `Documentation/admin-guide/sysctl/kernel.rst`):
`on` = userspace may read/write kmsg without the default rate limit;
`ratelimited` = printk from userspace is throttled.

**Catch on this ROM:** `vendor/etc/init/hw/init.target.rc` `on early-init`
does `write /proc/sys/kernel/printk_devkmsg ratelimited`. So even if ABL
puts `printk.devkmsg=on` on cmdline, Honor init resets it as soon as
userspace starts. The HIMNTN effect, if any, lasts only from kernel start
until `early-init`.

Bit is **1** now → ABL does **not** add the token; init still writes
`ratelimited`. Enabling the *effect* (`--enable printk_devkmsg`) clears the
bit. Low diagnostic value on this build unless you also stop init from
overwriting the sysctl.

---

### `tologpart` — item `0x03` (3) — currently **off**

ABL appends ` androidboot.log.tologpart=1` → property `ro.boot.log.tologpart`.

`system/etc/init/hilogcat.rc`:

```
on property:ro.boot.log.tologpart=1
    mkdir /log/android_logs
    start applogtologpart   # logcatz → /log/android_logs/applogcat-log
```

`/log` is the dedicated ext4 partition `by-name/log` (fstab.qcom), mounted
rw from several init files (`init.manufacture.rc`, charger, `bms_nvm.rc`).
Default applog goes to **`/data/log/android_logs`** (userdata). With this bit,
a second logcatz writes the same applog onto **`/log`**, which survives
userdata wipes / factory-ish data formats (recovery still has `/log`).

**On:** extra persistent applog on the `log` partition (10 zip files, 5 MB
each via `logcatz -z 10 -n 5`).

**Off (now):** only `/data/log/...` if other logcat services are started.

Same ABL also registers `fastboot oem applogtologpart`. Low-ish risk;
fills `/log`.

---

### `labexternal` — item `0x04` (4) — currently **off** (`ro.boot.labexternal=false`)

ABL writes `androidboot.labexternal=true` or `=false` every boot (both
branches). This is Honor’s “lab bench / external debug” switch. Fastboot
also has `oem labexternal`.

**`false` (now) — retail-like SSR:**

- `vendor.ssr.restart_level=ALL_ENABLE` → `ssr_setup` **restarts** crashed
  modem/Wi‑Fi/etc. instead of leaving them down for a dump.
- WLAN CNSS `recovery` sysfs = 1 (driver tries to recover).
- If `persist.sys.msc.debug.on=1`: `dload_mode=both` (mini+full mix).

**`true` — lab:**

- `vendor.ssr.restart_level=N/A` → subsystems **do not auto-restart** on
  crash (stay down so ramdumps can be collected).
- CNSS `recovery` = 0.
- USB (`init.honor.usb.rc` on `ro.hardware=qcom`): switch diag descriptors
  from Honor (`honor`, set at `early-init`) to **Qualcomm** (`qcom`), and
  `sys.adb.authpass=1` (ADB auth bypass for factory/lab). Manufacture USB
  composition then uses QCOM VID/PID `05C6:90DB` instead of Honor gadget.
- If `persist.sys.msc.debug.on=1`: `dload_mode=full` (full ramdump, not mini).

Factory `ro.runmode=factory` already forces the lab-like SSR path regardless
of this bit. **High risk** on a daily driver: modem/Wi‑Fi may not come back
after SSR; USB/diag identity changes.

---

### `maxcpus_2` — item `0x08` (8) — currently **off**

ABL appends ` maxcpus=2`. Standard kernel parameter: only CPU0+CPU1 are
brought up. The rest stay offline. **Do not enable** unless you are
debugging hotplug/bring-up. High risk (performance, thermal, some HALs).

---

### `on_failure_panic` — item `0x09` (9), **inverted** — effect currently **on**

When the **bit is 0** (now), ABL appends ` OnFailurePanic` to cmdline.
When the bit is 1, the token is omitted.

No init.rc / module / uncompressed kernel string on this ROM consumes it.
It is a leftover Honor/Huawei cmdline hook (older platforms paniced the
kernel on some driver failures instead of continuing). On this Qualcomm
6.6 kernel it is **likely a no-op**, but it still sits on cmdline. Treat
`--disable on_failure_panic` (which **sets** item 9) as “remove the token”;
do not expect a user-visible change unless a still-packed kernel option
exists.

---

### `uart_earlycon` — item `0x16` (22) — currently **off**

When on, ABL picks a chip-specific string table (`WAIPIO`…`BONITO`/…) and
appends UART/earlycon, for example:

- `msm_geni_serial.con_enabled=1 earlycon=msm_geni_serial,0x00……`
- or `console=ttyMSM0,115200n8 earlycon=qcom_geni,0x00……`

When off, it uses the “disabled” table (`con_enabled=0` / no extra console).
This device’s cmdline already has `console=ttynull` from DTB — enabling
this fights that (real UART vs null console).

Also **gates** `androidboot.logcat.kmsg=`: ABL only emits that token if this
bit is on **and** at least one of items 40–42 is on.

**High risk:** can stall boot on a missing UART, leak console, change
`console=` vs `ttynull`.

---

### `logcat_kmsg_b2/b1/b0` — items `0x28/0x29/0x2a` (40/41/42) — currently **off**

Three bits plus `uart_earlycon` build `androidboot.logcat.kmsg=<E|W|I|D|V>`.
ABL `fastboot oem logcat2kmsg [E/W/I/D/V/OFF]` writes the same field.
Selector 0 or UART off → no token.

`hilogcat.rc`:

```
on property:ro.boot.logcat.kmsg=*
    setprop persist.log.tag ${ro.boot.logcat.kmsg}
    start logcat2kmsg          # logcat -f /dev/kmsg
```

`persist.log.tag` is Android’s **global default log level** (Error / Warn /
Info / Debug / Verbose). `logcat -f /dev/kmsg` then mirrors that logcat
stream into the kernel ring (needs a large `log_buf_len` or it wraps even
faster).

`init.qcom.sh` and `logctl_service.sh` also, if `ro.boot.logcat.kmsg` is
set, poke `/proc/sys/kernel/printk` (`4 3 1 7` or
`consolelevel consolelevel-1`).

Exact E/W/I/D/V encoding of the three bits was not fully recovered (PIC
string table). Use ABL’s `oem logcat2kmsg` mentally: OFF = all zero / no
UART; non-zero = one of E/W/I/D/V. **Do not enable together with UART
unless you want logcat flooding kmsg.**

---

### `console_level_b3..b0` — items `0x2b`–`0x2e` (43–46) — currently **off**

Four bits → integer `androidboot.console.level=N` (0–15). ABL also has
`oem console_level`.

`init.qcom.sh` / `logctl_service.sh`:

```
consolelevel=`getprop ro.boot.console.level`
echo "$consolelevel" > /proc/sys/kernel/printk
```

That sysctl is `console_loglevel default_message_loglevel
minimum_console_loglevel default_console_loglevel`. Writing a single
integer sets **console_loglevel** (what goes to the serial/console).
User builds default to `4 4 1 4` (warning); userdebug/eng to `6 6 1 7`.

If both `console.level` and `logcat.kmsg` are set, scripts write
`consolelevel  consolelevel-1`.

Without the property (now), printk level stays at the `ro.build.type`
default from `init.qcom.sh`.

---

### `serial_bypass` — item `0x07` (7) — currently **off**

Two ABL roles share this bit.

**1. `ReadSerialNum` (LinuxLoader)** — fills `androidboot.serialno=`.

- Bit **off (now):** try SN from oeminfo (`GetSnFromOeminfo` / `ReadSnNumber`),
  then fall back to chip/board serial (`ChipInfo`, “Error Finding board
  serial num”).
- Bit **on** (and an internal “use chip serial” flag): **skip oeminfo SN**
  and go straight to chip/board serial. Lab units sometimes want the fuse
  serial instead of the factory-programmed one.

**2. BootDetector** — see next item; bit 7 **or** bit 31 arms the extra path.

Changing this can change `ro.boot.serialno` / `ro.serialno` vs what
userdata and attestations expect. High risk.

---

### `boot_detector` — item `0x1f` (31) — currently **off**

Honor ABL **BootDetector**: boot-loop watchdog. Logs talk about DDR/SMEM,
slot `boot_a`/`boot_b`, and “disable bootdetector recovery” during
upgrade, rollback, and a fastboot command.

When **item 31 or item 7 is set**, ABL clears two flags on the LinuxLoader
object (offsets `+0x1a8`, `+0x1ac`) — the same flags other paths set to
**disable** recovery. Net: keep boot-detector recovery **armed**.

When **both bits are off (now)**, that “re-arm” path is skipped; whatever
default/upgrade/fastboot last wrote to those flags stands.

Practical effect if armed: repeated failed boots can force recovery /
slot switch. If disarmed (OTA, rollback, `fastboot` disable): ABL will not
use that watchdog. Do not enable on a device you are deliberately
boot-looping in fastboot.

---

### `fastboot_gate` — item `0x0a` (10) — currently **off**

Used inside ABL’s fastboot dispatcher (`FUN_00052f28`) together with the
battery-voltage warning and the `Command not allowed` ACL. The bit is
stored inverted into an internal flag (`DAT_001d3484 = (item10 == 0)`).

Exact user-visible mapping was not fully named (no oem help string). Leave
it **off**. Flipping it can change which oem commands are accepted while
unlocked — including making more (or fewer) commands hit `Command not
allowed`.

---

### `factory_marker` — item `0x01` (1) — currently **on**

Not a cmdline token. `xmntn -h 1` (`HimntnHandle::HandleFlow`):

- Commercial/user build: does not rewrite HIMNTN.
- Non-commercial, **this bit on:** log `partition has been correct`, skip
  write.
- Non-commercial, **bit off:** overwrite the mask with a baked default
  (`0x1C85F6FE00` if `ro.runmode=factory`, else `0x485B6FE00`) OR’d with
  `0x4849400000000000`.

Keep it **on** so a future non-user build cannot stomp a hand-edited mask.

---

## Combined picture on this phone (now)

| name | item | bit | effect |
|---|---|---|---|
| factory_marker | 1 | 1 | xmntn will not factory-reset the mask |
| tologpart | 3 | 0 | applog stays on `/data/log`, not `/log` |
| labexternal | 4 | 0 | SSR restart enabled, Honor USB diag, `dload_mode` not forced full |
| serial_bypass | 7 | 0 | serialno from oeminfo first |
| maxcpus_2 | 8 | 0 | all CPUs |
| on_failure_panic | 9 | 0 | token `OnFailurePanic` **is** on cmdline (likely unused) |
| fastboot_gate | 10 | 0 | default ABL fastboot gating |
| uart_earlycon | 22 | 0 | no extra UART; `console=ttynull` from DTB |
| log_buf_len_4m | 28 | 0 | printk 1M |
| printk_devkmsg | 29 | 1 | no `devkmsg=on`; init sets `ratelimited` anyway |
| boot_detector | 31 | 0 | extra BootDetector re-arm skipped |
| logcat_kmsg_* | 40–42 | 0 | no `logcat -f /dev/kmsg` from this path |
| console_level_* | 43–46 | 0 | printk levels from `ro.build.type` (user → warning) |

Items on with no ABL name: `11–13, 16, 21, 23–27, 30, 32–38`. Leave them.

## Safe change for full kernel logs

```bash
./himntn_rawdump.py --enable log_buf_len_4m
# paste the printed adb exec-out su -c '…' command
# reboot
# confirm: tr ' ' '\n' < /proc/cmdline | grep log_buf_len
# should show log_buf_len=1M then log_buf_len=4M
./collect_current_boot_logs.sh
```

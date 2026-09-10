# Cortex OS Lab

**Goal:** treat the operating system as an AI — not an app sitting on top of Android.

**Reality check:** you cannot delete Linux from a running Android emulator and drop in a brand-new kernel overnight. Android *is* a Linux kernel plus a huge userspace (init, zygote, ART, Binder). What you *can* do is:

1. Boot a **rooted** Android emulator so you have `su`, ADB root, and kernel logs.
2. Live inside that Linux userspace.
3. Put an **AI control plane** in front of every decision (apps, files, network, power).
4. Slowly replace *userspace* pieces (init scripts, package manager, launcher, policy) with Cortex.
5. Only later: custom kernel modules / a custom kernel image for the emulator (Goldfish / ranchu).

If the AI owns scheduling policy, permissions, UI, and recovery, the *experience* is an AI OS even while Linux still talks to hardware.

## Repo you already have

This account already contains many sibling labs (`synapse-aios`, `SentientOS`, `aether-ai-os-emulator`, `lumen-ai-os-lab`, …). Use **this** repo as the current lab so work does not fragment again.

## Best rooted emulator path (2026)

| Option | Root | Why use it |
|---|---|---|
| **Android Studio AVD + Magisk / rootAVD** | Yes (you add it) | Official emulator, Goldfish/ranchu kernel you can inspect and later replace |
| **Android Studio AOSP / Google APIs image** | `adb root` works on many images | Fastest way to a root shell; no Play Store |
| **Genymotion Desktop** | Older images rooted; newer images can be rooted dynamically | Fast VMs, good for QA |
| **Nux Emulator** | Magisk / KernelSU / APatch | Linux-host emulator with explicit root support |
| **Waydroid** | Possible with Magisk in the container | Near-native Android on Linux, shares host kernel |
| **QEMU + Android-x86 / Bliss OS** | You control the disk | Closest to “install our own OS image” |

**Recommended lab start:** Android Studio emulator, **Google APIs** (not Play) system image, x86_64 or arm64, then Magisk via rootAVD or KernelSU GKI swap for Play images.

Related tooling:
- rootAVD — Magisk on AVDs
- android_emuroot — live root via QEMU GDB (research only)
- fries/android-emulator-root — custom emulator kernels + `su`
- AOSP goldfish kernel: `https://android.googlesource.com/kernel/goldfish`

## Phases

### Phase 0 — Lab boots
- Install Android Studio + platform-tools.
- Create AVD: API 34+ Google APIs, x86_64 or arm64.
- `adb root && adb shell` → `#` prompt.
- Collect `/proc/version`, `uname -a`, `getprop ro.kernel.qemu`.

### Phase 1 — Cortex supervisor (this repo)
Python agent on the **host** talks to the emulator over ADB.
It is the OS brain: observe, decide, act, remember.

```
host: cortex/supervisor.py  --adb-->  emulator Linux
```

### Phase 2 — Userspace takeover
- Custom launcher / lockscreen that is only Cortex.
- Policy engine instead of Settings.
- Init overlay: Cortex starts after `zygote`, owns foreground.

### Phase 3 — Kernel interface (not a full swap)
- Custom goldfish/ranchu kernel with extra syscalls or a char device `/dev/cortex`.
- Kernel still schedules; Cortex decides *why*.

### Phase 4 — Own image
- Build an AOSP product `cortex_x86_64` or a QEMU disk that boots Cortex userspace on Linux.
- Long term: microkernel / unikernel research. That is years, not a weekend.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# emulator must be running and visible to adb
adb devices
python3 cortex/supervisor.py --once
```

## Layout

```
cortex/           AI control plane (host-side)
docs/             emulator + kernel notes
scripts/          ADB helpers
```

## License

MIT. Research / education only. Do not use root tooling to attack devices you do not own.

# Emulator lab

## Path A — fastest root shell (recommended first hour)

1. Install Android Studio + SDK platform-tools.
2. AVD Manager → Create Virtual Device.
3. System image: **Google APIs** (not Google Play). Play images block `adb root`.
4. Start the AVD.
5. On the host:

```bash
adb devices
adb root
adb shell
# you want a # prompt and id → uid=0(root)
cat /proc/version
uname -a
getprop ro.kernel.qemu
ls /sys /proc /dev
```

That *is* Linux. Android userland sits on top of it.

## Path B — Magisk on the official emulator

Use rootAVD (Magisk) against the AVD system image, then reboot the emulator.
After Magisk is installed you get `su` even on some Play images.

## Path C — KernelSU on Play images

Replace `kernel-ranchu` in the emulator system image with a KernelSU-enabled GKI build matching the Android version. Higher risk of boot loops. Snapshot the AVD first.

## Path D — Genymotion

Personal-use Desktop. Older API images ship rooted. Newer images can be rooted dynamically from Genymotion docs. Good when Android Studio is too heavy.

## Path E — own disk (closest to “replace the OS”)

QEMU + Android-x86 or Bliss OS, or a custom AOSP lunch target. You own the disk image. Cortex userspace can become `init`.

## What “replace Linux” actually means here

| Layer | Swap now? | Plan |
|---|---|---|
| Hardware + virt (QEMU/KVM) | No | Keep |
| Linux kernel (goldfish/ranchu) | Not yet | Custom kernel later |
| init / zygote / ART | Later | Overlay, then replace |
| Launcher, Settings, PackageManager | Yes, Phase 2 | Cortex UI + policy |
| Decision making | Yes, Phase 1 | supervisor.py |

You replace the *mind* first. The kernel stays the body until you can write one.

#!/usr/bin/env bash
set -euo pipefail
adb start-server >/dev/null
echo "=== devices ==="
adb devices -l
echo "=== root? ==="
adb root || true
sleep 1
echo "=== identity ==="
adb shell id || true
echo "=== kernel ==="
adb shell uname -a || true
adb shell cat /proc/version || true
echo "=== qemu? ==="
adb shell getprop ro.kernel.qemu || true
adb shell getprop ro.build.fingerprint || true

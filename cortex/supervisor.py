#!/usr/bin/env python3
"""Cortex supervisor — the OS brain living on the host, acting through ADB.

This is Phase 1. It does not replace the kernel. It *is* the policy layer:
observe the guest Linux, decide what matters, write memory, optionally act.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from cortex.adb import Adb, AdbError

MEMORY = Path(__file__).resolve().parent.parent / "state" / "memory.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def decide(snapshot: dict[str, str]) -> dict:
    """Tiny policy brain. Swap this for a real model later."""
    uid = snapshot.get("id", "")
    rooted = uid.startswith("uid=0") or "uid=0(" in uid
    kernel = snapshot.get("kernel", "")
    qemu = snapshot.get("qemu", "")
    return {
        "rooted": rooted,
        "in_emulator": qemu in {"1", "true"} or "qemu" in kernel.lower() or "goldfish" in kernel.lower(),
        "intent": "observe" if rooted else "gain_root_shell",
        "note": (
            "Root shell present. Cortex can own userspace policy."
            if rooted
            else "No uid=0 yet. Use Google APIs image + adb root, or Magisk/rootAVD."
        ),
    }


def remember(event: dict) -> None:
    MEMORY.parent.mkdir(parents=True, exist_ok=True)
    with MEMORY.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event) + "\n")


def tick(adb: Adb) -> dict:
    snap = adb.snapshot()
    policy = decide(snap)
    event = {"ts": utc_now(), "snapshot": snap, "policy": policy}
    remember(event)
    return event


def main() -> int:
    parser = argparse.ArgumentParser(description="Cortex OS supervisor")
    parser.add_argument("--serial", help="adb device serial")
    parser.add_argument("--once", action="store_true", help="one tick then exit")
    parser.add_argument("--interval", type=float, default=15.0)
    args = parser.parse_args()

    adb = Adb(serial=args.serial)
    try:
        devices = adb.devices()
    except AdbError as exc:
        print(f"adb failed: {exc}")
        return 1

    if not devices:
        print("No emulator/device. Start an AVD first: emulator -avd <name>")
        return 2

    if not args.serial:
        adb.serial = devices[0]
    print(f"target={adb.serial} devices={devices}")
    adb.try_root()

    while True:
        event = tick(adb)
        pol = event["policy"]
        print(json.dumps({"ts": event["ts"], **pol}, indent=2))
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())

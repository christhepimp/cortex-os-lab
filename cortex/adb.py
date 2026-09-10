"""Thin ADB wrapper. Requires platform-tools on PATH."""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


class AdbError(RuntimeError):
    pass


@dataclass
class Adb:
    serial: str | None = None
    timeout: int = 20

    def _bin(self) -> str:
        path = shutil.which("adb")
        if not path:
            raise AdbError("adb not on PATH. Install Android platform-tools.")
        return path

    def _base(self) -> list[str]:
        cmd = [self._bin()]
        if self.serial:
            cmd += ["-s", self.serial]
        return cmd

    def run(self, *args: str) -> str:
        proc = subprocess.run(
            self._base() + list(args),
            capture_output=True,
            text=True,
            timeout=self.timeout,
        )
        if proc.returncode != 0:
            raise AdbError(proc.stderr.strip() or proc.stdout.strip() or "adb failed")
        return proc.stdout.strip()

    def devices(self) -> list[str]:
        out = self.run("devices")
        lines = [ln for ln in out.splitlines()[1:] if ln.strip()]
        return [ln.split()[0] for ln in lines if "device" in ln.split()]

    def shell(self, command: str) -> str:
        return self.run("shell", command)

    def try_root(self) -> bool:
        try:
            self.run("root")
            return True
        except AdbError:
            return False

    def snapshot(self) -> dict[str, str]:
        keys = {
            "uname": "uname -a",
            "kernel": "cat /proc/version",
            "id": "id",
            "qemu": "getprop ro.kernel.qemu",
            "fingerprint": "getprop ro.build.fingerprint",
            "abi": "getprop ro.product.cpu.abi",
            "uptime": "cat /proc/uptime",
        }
        data: dict[str, str] = {}
        for name, cmd in keys.items():
            try:
                data[name] = self.shell(cmd)
            except AdbError as exc:
                data[name] = f"error: {exc}"
        return data

#!/usr/bin/env python3
"""PhonixCast CLI.

Herramienta ligera para iniciar transmisión de pantalla por USB usando adb + scrcpy.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:
    name: str
    bitrate: str
    max_fps: int
    codec: str


PROFILES: dict[str, Profile] = {
    "balanced": Profile("balanced", bitrate="8M", max_fps=60, codec="h264"),
    "low-latency": Profile("low-latency", bitrate="6M", max_fps=45, codec="h264"),
    "ultra-low-latency": Profile(
        "ultra-low-latency", bitrate="4M", max_fps=30, codec="h264"
    ),
}


def _require_binary(binary: str) -> None:
    if shutil.which(binary) is None:
        raise RuntimeError(f"No se encontró '{binary}' en PATH.")


def run_command(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=False,
        text=True,
        capture_output=capture,
    )


def list_devices() -> list[str]:
    result = run_command(["adb", "devices"], capture=True)
    if result.returncode != 0:
        raise RuntimeError(f"Fallo ejecutando adb devices: {result.stderr.strip()}")

    devices: list[str] = []
    for line in result.stdout.splitlines()[1:]:
        parts = line.strip().split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def set_stay_awake(device: str, enabled: bool) -> None:
    value = "3" if enabled else "0"
    cmd = ["adb", "-s", device, "shell", "settings", "put", "global", "stay_on_while_plugged_in", value]
    result = run_command(cmd)
    if result.returncode != 0:
        raise RuntimeError("No se pudo configurar stay_awake en el dispositivo.")


def start_stream(args: argparse.Namespace) -> int:
    profile = PROFILES[args.profile]
    devices = list_devices()

    if not devices:
        print("No se encontraron dispositivos Android en modo 'device'.", file=sys.stderr)
        return 2

    device = args.serial or devices[0]
    if device not in devices:
        print(f"El dispositivo solicitado ({device}) no está disponible.", file=sys.stderr)
        return 2

    if args.stay_awake:
        set_stay_awake(device, True)

    cmd = [
        "scrcpy",
        "--serial",
        device,
        "--video-bit-rate",
        profile.bitrate,
        "--max-fps",
        str(profile.max_fps),
        "--video-codec",
        profile.codec,
    ]

    if args.max_size:
        cmd.extend(["--max-size", str(args.max_size)])

    if args.turn_screen_off:
        cmd.append("--turn-screen-off")

    if args.no_audio:
        cmd.append("--no-audio")

    print(f"Iniciando transmisión con perfil '{profile.name}' en dispositivo {device}...")
    result = run_command(cmd)

    if args.stay_awake:
        try:
            set_stay_awake(device, False)
        except RuntimeError:
            print(
                "Advertencia: no se pudo restaurar stay_awake automáticamente.",
                file=sys.stderr,
            )

    return result.returncode


def print_profiles() -> int:
    print("Perfiles disponibles:")
    for profile in PROFILES.values():
        print(
            f"- {profile.name}: bitrate={profile.bitrate}, "
            f"max_fps={profile.max_fps}, codec={profile.codec}"
        )
    return 0


def print_devices() -> int:
    devices = list_devices()
    if not devices:
        print("Sin dispositivos conectados.")
        return 0

    print("Dispositivos detectados:")
    for serial in devices:
        print(f"- {serial}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phonixcast",
        description="Transmisión de pantalla Android por USB (adb + scrcpy).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("profiles", help="Muestra perfiles predefinidos")
    subparsers.add_parser("devices", help="Lista dispositivos disponibles")

    start = subparsers.add_parser("start", help="Inicia la transmisión")
    start.add_argument("--profile", choices=PROFILES.keys(), default="balanced")
    start.add_argument("--serial", help="Serial adb específico")
    start.add_argument("--max-size", type=int, help="Resolución máxima del video")
    start.add_argument("--turn-screen-off", action="store_true")
    start.add_argument("--stay-awake", action="store_true")
    start.add_argument("--no-audio", action="store_true")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command in {"devices", "start"}:
            _require_binary("adb")
        if args.command == "start":
            _require_binary("scrcpy")

        if args.command == "profiles":
            return print_profiles()
        if args.command == "devices":
            return print_devices()
        if args.command == "start":
            return start_stream(args)

        parser.print_help()
        return 1
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from .config import AppConfig
from .executor import CommandRunner


def build_parser() -> argparse.ArgumentParser:
    import argparse

    parser = argparse.ArgumentParser(
        prog="kali-forge",
        description="A modular, local-first security testing workflow toolkit.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("version", help="Show the installed version.")

    run_parser = subparsers.add_parser("run", help="Execute an allowlisted command safely.")
    run_parser.add_argument("argv", nargs="+", help="Executable and arguments to run.")

    config_parser = subparsers.add_parser("config", help="Display configuration details.")
    config_parser.add_argument(
        "--show",
        action="store_true",
        help="Print the current effective configuration as JSON.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        print("kali-forge 0.1.0")
        return 0

    if args.command == "run":
        runner = CommandRunner(AppConfig())
        try:
            result = runner.run(args.argv)
        except (FileNotFoundError, ValueError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2

        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        return result.returncode

    if args.command == "config":
        config = AppConfig()
        payload = {
            "working_directory": str(config.workdir),
            "allowed_commands": list(config.allowed_commands),
            "timeout_seconds": config.timeout_seconds,
            "max_output_bytes": config.max_output_bytes,
            "environment_allowlist": list(config.environment_allowlist),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2

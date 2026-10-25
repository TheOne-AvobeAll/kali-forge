from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .config import AppConfig
from .executor import CommandRunner
from .workflow import WorkflowSpec, get_workflow, list_workflows


def build_parser() -> argparse.ArgumentParser:
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

    workflow_parser = subparsers.add_parser("workflow", help="Manage reusable workflow templates.")
    workflow_subparsers = workflow_parser.add_subparsers(dest="workflow_command", required=True)
    workflow_subparsers.add_parser("list", help="List available workflow templates.")

    show_parser = workflow_subparsers.add_parser("show", help="Show a workflow template definition.")
    show_parser.add_argument("name", help="Name of the workflow template.")

    run_workflow_parser = workflow_subparsers.add_parser("run", help="Execute a built-in workflow.")
    run_workflow_parser.add_argument("name", help="Name of the workflow template.")

    return parser


def _print_workflow_list() -> None:
    for workflow in list_workflows():
        print(f"- {workflow.name}: {workflow.description}")


def _print_workflow_details(name: str) -> None:
    workflow = get_workflow(name)
    print(json.dumps(workflow.to_dict(), indent=2, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> int:
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

    if args.command == "workflow":
        if args.workflow_command == "list":
            _print_workflow_list()
            return 0

        if args.workflow_command == "show":
            _print_workflow_details(args.name)
            return 0

        if args.workflow_command == "run":
            workflow = get_workflow(args.name)
            runner = CommandRunner(AppConfig())
            for step in workflow.steps:
                command_parts = step.split()
                if not command_parts:
                    continue
                result = runner.run(command_parts)
                if result.stdout:
                    print(result.stdout, end="")
                if result.stderr:
                    print(result.stderr, end="", file=sys.stderr)
                if result.returncode != 0:
                    return result.returncode
            return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2

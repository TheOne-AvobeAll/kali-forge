from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


DANGEROUS_ARGUMENT_MARKERS = {
    ";",
    "&&",
    "||",
    "|",
    ">",
    ">>",
    "<",
    "<<",
    "2>",
    "2>>",
    "&",
    "$(",
    "`",
    "\\n",
    "\\r",
}


@dataclass(frozen=True)
class CommandPolicy:
    safe_commands: tuple[str, ...] = (
        "echo",
        "printf",
        "pwd",
        "ls",
        "cat",
        "grep",
        "which",
        "head",
        "tail",
        "wc",
        "uname",
        "true",
        "false",
    )
    blocked_commands: tuple[str, ...] = (
        "bash",
        "sh",
        "zsh",
        "dash",
        "python",
        "python3",
        "perl",
        "ruby",
        "node",
    )
    blocked_flags: tuple[str, ...] = (
        "-c",
        "--eval",
        "-e",
        "/bin/bash",
        "/bin/sh",
    )

    def is_safe_executable(self, executable_name: str) -> bool:
        name = executable_name.strip().lower()
        if not name:
            return False
        if name in self.blocked_commands:
            return False
        if name in self.safe_commands:
            return True
        return False

    def validate(self, argv: Sequence[str]) -> None:
        if not argv:
            raise ValueError("Command must include at least one argument.")

        for part in argv:
            value = str(part).strip()
            if not value:
                continue
            if any(marker in value for marker in DANGEROUS_ARGUMENT_MARKERS):
                raise ValueError(f"Command contains unsafe shell syntax: {value!r}")
            lowered = value.lower()
            if lowered in self.blocked_flags:
                raise ValueError(f"Command contains blocked execution flag: {value!r}")


def ensure_within_directory(target: str | Path, base_dir: str | Path) -> Path:
    """Resolve a target path and ensure it stays within the configured base directory."""
    base_path = Path(base_dir).expanduser().resolve()
    candidate = Path(target).expanduser().resolve(strict=False)

    try:
        candidate.relative_to(base_path)
    except ValueError as exc:
        raise ValueError(f"Path '{target}' escapes the allowed directory '{base_dir}'.") from exc

    return candidate


def validate_runtime_context() -> None:
    """Reject execution contexts that are too privileged or too open for local-first safe work."""
    if os.geteuid() == 0:
        raise PermissionError("Refusing to run in privileged root mode for local-first execution.")

    sensitive_vars = {
        "LD_PRELOAD",
        "LD_LIBRARY_PATH",
        "PYTHONPATH",
        "BASH_ENV",
        "ENV",
    }
    for key in sensitive_vars:
        if key in os.environ and os.environ.get(key):
            raise ValueError(f"Execution environment variable '{key}' is not allowed in safe mode.")

    if os.environ.get("HOME") is None:
        raise ValueError("HOME is required for safe execution context.")


def validate_command_arguments(arguments: Sequence[str]) -> tuple[str, ...]:
    """Reject empty or malformed command arguments as part of safe execution validation."""
    cleaned: list[str] = []
    for value in arguments:
        if value is None:
            raise ValueError("Command arguments must not be None.")
        normalized = str(value).strip()
        if not normalized:
            raise ValueError("Command arguments must not be empty.")
        if any(marker in normalized for marker in DANGEROUS_ARGUMENT_MARKERS):
            raise ValueError(f"Command argument contains unsafe shell syntax: {normalized!r}")
        cleaned.append(normalized)
    if not cleaned:
        raise ValueError("A command must include at least one argument.")
    return tuple(cleaned)


def validate_allowed_executable(
    executable: str | Path,
    allowed_commands: Iterable[str] | None = None,
    policy: CommandPolicy | None = None,
) -> Path:
    """Resolve an executable and ensure it is explicitly allowlisted."""
    name = str(executable).strip()
    if not name:
        raise ValueError("Executable path cannot be empty.")

    resolved = shutil.which(name)
    if resolved is None:
        raise FileNotFoundError(f"Executable '{name}' is not available on PATH.")

    executable_name = Path(resolved).name.lower()

    if policy is not None:
        if not policy.is_safe_executable(executable_name):
            raise ValueError(
                f"Executable '{executable_name}' is blocked by the safe execution policy."
            )

    if allowed_commands is not None:
        allowed = {candidate.lower() for candidate in allowed_commands if str(candidate).strip()}
        if executable_name not in allowed:
            raise ValueError(
                f"Executable '{executable_name}' is not in the configured allowlist."
            )

    return Path(resolved)


__all__ = [
    "CommandPolicy",
    "ensure_within_directory",
    "validate_runtime_context",
    "validate_command_arguments",
    "validate_allowed_executable",
]

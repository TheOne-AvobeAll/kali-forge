from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, Sequence


def ensure_within_directory(target: str | Path, base_dir: str | Path) -> Path:
    """Resolve a target path and ensure it stays within the configured base directory."""
    base_path = Path(base_dir).expanduser().resolve()
    candidate = Path(target).expanduser().resolve(strict=False)

    try:
        candidate.relative_to(base_path)
    except ValueError as exc:
        raise ValueError(f"Path '{target}' escapes the allowed directory '{base_dir}'.") from exc

    return candidate


def validate_command_arguments(arguments: Sequence[str]) -> tuple[str, ...]:
    """Reject empty or malformed command arguments as part of safe execution validation."""
    cleaned: list[str] = []
    for value in arguments:
        if value is None:
            raise ValueError("Command arguments must not be None.")
        normalized = str(value).strip()
        if not normalized:
            raise ValueError("Command arguments must not be empty.")
        cleaned.append(normalized)
    if not cleaned:
        raise ValueError("A command must include at least one argument.")
    return tuple(cleaned)


def validate_allowed_executable(
    executable: str | Path,
    allowed_commands: Iterable[str] | None = None,
) -> Path:
    """Resolve an executable and ensure it is explicitly allowlisted."""
    name = str(executable).strip()
    if not name:
        raise ValueError("Executable path cannot be empty.")

    resolved = shutil.which(name)
    if resolved is None:
        raise FileNotFoundError(f"Executable '{name}' is not available on PATH.")

    if allowed_commands is not None:
        allowed = {candidate.lower() for candidate in allowed_commands if str(candidate).strip()}
        if Path(resolved).name.lower() not in allowed:
            raise ValueError(
                f"Executable '{Path(resolved).name}' is not in the configured allowlist."
            )

    return Path(resolved)


__all__ = [
    "ensure_within_directory",
    "validate_command_arguments",
    "validate_allowed_executable",
]

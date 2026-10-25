from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Runtime defaults for the secure CLI layer."""

    workdir: Path = Path.cwd()
    allowed_commands: tuple[str, ...] = (
        "echo",
        "printf",
        "pwd",
        "ls",
        "python",
        "python3",
        "bash",
        "cat",
        "grep",
        "which",
    )
    timeout_seconds: int = 30
    max_output_bytes: int = 20_000
    environment_allowlist: tuple[str, ...] = (
        "PATH",
        "HOME",
        "TERM",
        "USER",
        "PYTHONPATH",
    )

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")
        if self.max_output_bytes <= 0:
            raise ValueError("max_output_bytes must be greater than zero.")
        object.__setattr__(self, "workdir", Path(self.workdir).expanduser().resolve())

    def to_dict(self) -> dict[str, object]:
        return {
            "working_directory": str(self.workdir),
            "allowed_commands": list(self.allowed_commands),
            "timeout_seconds": self.timeout_seconds,
            "max_output_bytes": self.max_output_bytes,
            "environment_allowlist": list(self.environment_allowlist),
        }


__all__ = ["AppConfig"]

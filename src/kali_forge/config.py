from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Application defaults for a secure, deterministic CLI runtime."""

    workdir: Path = Path.cwd()
    allowed_commands: tuple[str, ...] = (
        "echo",
        "printf",
        "pwd",
        "ls",
        "python",
        "python3",
        "bash",
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

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LabConfig:
    """Local lab configuration for an authorized environment."""

    name: str = "default-lab"
    workdir: str = "."
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
    allowed_paths: tuple[str, ...] = field(default_factory=lambda: (".",))

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Lab name cannot be empty.")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")
        if self.max_output_bytes <= 0:
            raise ValueError("max_output_bytes must be greater than zero.")
        if not self.allowed_paths:
            raise ValueError("At least one allowed path must be configured.")

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "workdir": self.workdir,
            "allowed_commands": list(self.allowed_commands),
            "timeout_seconds": self.timeout_seconds,
            "max_output_bytes": self.max_output_bytes,
            "environment_allowlist": list(self.environment_allowlist),
            "allowed_paths": list(self.allowed_paths),
        }


def save_default_lab_config(path: str | Path) -> LabConfig:
    config = LabConfig()
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(config.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return config


def load_lab_config(path: str | Path) -> LabConfig:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return LabConfig(
        name=payload.get("name", "default-lab"),
        workdir=payload.get("workdir", "."),
        allowed_commands=tuple(payload.get("allowed_commands", ())),
        timeout_seconds=int(payload.get("timeout_seconds", 30)),
        max_output_bytes=int(payload.get("max_output_bytes", 20_000)),
        environment_allowlist=tuple(
            payload.get("environment_allowlist", ("PATH", "HOME", "TERM", "USER", "PYTHONPATH"))
        ),
        allowed_paths=tuple(payload.get("allowed_paths", (".",))),
    )


__all__ = ["LabConfig", "save_default_lab_config", "load_lab_config"]

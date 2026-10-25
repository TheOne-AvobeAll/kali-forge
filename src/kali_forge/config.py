from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .policy import PolicyProfile, get_policy


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
    social_policy: str = "brand-protection"
    social_allowed_sources: tuple[str, ...] = (
        "twitter",
        "x",
        "linkedin",
        "instagram",
        "mastodon",
        "reddit",
        "discord",
    )
    social_max_retention_days: int = 30

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")
        if self.max_output_bytes <= 0:
            raise ValueError("max_output_bytes must be greater than zero.")
        if self.social_max_retention_days <= 0:
            raise ValueError("social_max_retention_days must be greater than zero.")
        object.__setattr__(self, "workdir", Path(self.workdir).expanduser().resolve())
        policy = get_policy(self.social_policy)
        object.__setattr__(self, "social_policy", policy.name)

    def to_dict(self) -> dict[str, object]:
        return {
            "working_directory": str(self.workdir),
            "allowed_commands": list(self.allowed_commands),
            "timeout_seconds": self.timeout_seconds,
            "max_output_bytes": self.max_output_bytes,
            "environment_allowlist": list(self.environment_allowlist),
            "social_policy": self.social_policy,
            "social_allowed_sources": list(self.social_allowed_sources),
            "social_max_retention_days": self.social_max_retention_days,
        }


__all__ = ["AppConfig"]

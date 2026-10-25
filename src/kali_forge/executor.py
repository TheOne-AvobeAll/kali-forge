from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Sequence

from .config import AppConfig
from .security import ensure_within_directory, validate_allowed_executable, validate_command_arguments


@dataclass(frozen=True)
class ExecutionResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


class CommandRunner:
    """Execute allowlisted commands with deterministic runtime guards."""

    def __init__(self, config: AppConfig | None = None):
        self.config = config or AppConfig()

    def run(self, argv: Sequence[str]) -> ExecutionResult:
        if not argv:
            raise ValueError("A command must be passed to run().")

        cleaned = validate_command_arguments(argv)
        executable = validate_allowed_executable(cleaned[0], self.config.allowed_commands)

        ensure_within_directory(self.config.workdir, self.config.workdir)

        env = self._build_environment()
        try:
            completed = subprocess.run(
                [str(executable), *list(cleaned[1:])],
                capture_output=True,
                text=True,
                shell=False,
                cwd=str(self.config.workdir),
                timeout=self.config.timeout_seconds,
                env=env,
            )
            stdout = completed.stdout[: self.config.max_output_bytes]
            stderr = completed.stderr[: self.config.max_output_bytes]
            return ExecutionResult(
                command=cleaned,
                returncode=completed.returncode,
                stdout=stdout,
                stderr=stderr,
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = (exc.stdout or "")[: self.config.max_output_bytes]
            stderr = (exc.stderr or "")[: self.config.max_output_bytes]
            return ExecutionResult(
                command=cleaned,
                returncode=124,
                stdout=stdout,
                stderr=stderr,
                timed_out=True,
            )

    def _build_environment(self) -> dict[str, str]:
        sanitized: dict[str, str] = {}
        for key in self.config.environment_allowlist:
            value = os.environ.get(key)
            if value is not None:
                sanitized[key] = value
        sanitized["PATH"] = os.environ.get("PATH", "")
        return sanitized


__all__ = ["CommandRunner", "ExecutionResult"]

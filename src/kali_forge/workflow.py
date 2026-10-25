from __future__ import annotations

import shlex
from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowSpec:
    """A deterministic workflow made of allowlisted shell steps."""

    name: str
    description: str
    steps: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Workflow name must not be empty.")
        if not self.description.strip():
            raise ValueError("Workflow description must not be empty.")
        if not self.steps:
            raise ValueError("Workflow steps must not be empty.")
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "description", self.description.strip())
        object.__setattr__(self, "steps", tuple(str(step).strip() for step in self.steps if str(step).strip()))

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "steps": list(self.steps),
        }


BUILTIN_WORKFLOWS: dict[str, WorkflowSpec] = {
    "hello-world": WorkflowSpec(
        name="hello-world",
        description="A minimal workflow that prints a greeting and reports the current directory.",
        steps=("echo 'hello from kali-forge'", "pwd"),
    ),
    "list-env": WorkflowSpec(
        name="list-env",
        description="Displays a safe view of the environment and execution context.",
        steps=("python -c \"import os; print(os.environ.get('PATH',''))\"", "echo user-ready"),
    ),
}


def parse_command_step(step: str) -> list[str]:
    """Parse a workflow step with shell-like quoting support."""
    cleaned = str(step).strip()
    if not cleaned:
        raise ValueError("Workflow step cannot be empty.")
    try:
        tokens = shlex.split(cleaned, posix=True)
    except ValueError as exc:
        raise ValueError(f"Invalid workflow step '{step}'.") from exc
    if not tokens:
        raise ValueError(f"Workflow step '{step}' produced no executable tokens.")
    return tokens


def list_workflows() -> tuple[WorkflowSpec, ...]:
    return tuple(BUILTIN_WORKFLOWS.values())


def get_workflow(name: str) -> WorkflowSpec:
    workflow = BUILTIN_WORKFLOWS.get(name.strip())
    if workflow is None:
        raise ValueError(f"Workflow '{name}' is not available.")
    return workflow


__all__ = ["WorkflowSpec", "parse_command_step", "list_workflows", "get_workflow"]

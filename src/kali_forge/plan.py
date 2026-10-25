from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PlanStep:
    """Single phase inside a local execution plan."""

    name: str
    command: str
    allow_failure: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Plan step name must not be empty.")
        if not self.command.strip():
            raise ValueError("Plan step command must not be empty.")
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "command", self.command.strip())

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "command": self.command,
            "allow_failure": self.allow_failure,
        }


@dataclass(frozen=True)
class ExecutionPlan:
    """A persisted execution plan for deterministic local workflows."""

    name: str = "default-plan"
    description: str = "Default local execution plan"
    steps: tuple[PlanStep, ...] = (
        PlanStep(name="greet", command="echo hello from kali-forge"),
        PlanStep(name="cwd", command="pwd"),
    )

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Plan name must not be empty.")
        if not self.description.strip():
            raise ValueError("Plan description must not be empty.")
        if not self.steps:
            raise ValueError("Plan steps must not be empty.")

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
        }


def save_default_plan(path: str | Path) -> ExecutionPlan:
    plan = ExecutionPlan()
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(plan.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return plan


def load_plan(path: str | Path) -> ExecutionPlan:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    steps = tuple(
        PlanStep(
            name=step.get("name", "unnamed-step"),
            command=step.get("command", ""),
            allow_failure=bool(step.get("allow_failure", False)),
        )
        for step in payload.get("steps", [])
    )
    return ExecutionPlan(
        name=payload.get("name", "default-plan"),
        description=payload.get("description", "Default local execution plan"),
        steps=steps,
    )


__all__ = ["PlanStep", "ExecutionPlan", "save_default_plan", "load_plan"]

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def default_audit_path(base_dir: str | Path = ".kali-forge") -> Path:
    """Return the default JSONL audit log path for plan execution history."""
    path = Path(base_dir) / "audit" / "plan-runs.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def read_audit_entries(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Read JSONL audit entries from disk."""
    destination = Path(path) if path is not None else default_audit_path()
    if not destination.exists():
        return []

    entries: list[dict[str, Any]] = []
    with destination.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                entries.append(json.loads(stripped))
            except json.JSONDecodeError:
                continue
    return entries


def summarize_audit_entries(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Collapse audit entries into a concise execution summary."""
    if not entries:
        return {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "plans": [],
            "last_timestamp": None,
        }

    plans = sorted({entry.get("plan_name", "unknown-plan") for entry in entries})
    successful = sum(1 for entry in entries if str(entry.get("status", "")).lower() == "success")
    failed = sum(1 for entry in entries if str(entry.get("status", "")).lower() == "failed")
    timestamps = [entry.get("timestamp") for entry in entries if entry.get("timestamp")]

    return {
        "total_runs": len(entries),
        "successful_runs": successful,
        "failed_runs": failed,
        "plans": plans,
        "last_timestamp": max(timestamps) if timestamps else None,
    }


def append_audit_entry(entry: dict[str, Any], path: str | Path | None = None) -> Path:
    """Append a single audit record to a JSONL log file."""
    destination = Path(path) if path is not None else default_audit_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return destination


def build_audit_entry(
    plan_name: str,
    step_name: str,
    command: str,
    returncode: int,
    stdout: str,
    stderr: str,
    timed_out: bool,
    status: str | None = None,
) -> dict[str, Any]:
    """Create a normalized execution record for logging."""
    normalized_status = status or ("success" if returncode == 0 else "failed")
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "plan_name": str(plan_name).strip() or "unknown-plan",
        "step_name": str(step_name).strip() or "unnamed-step",
        "command": str(command).strip(),
        "returncode": int(returncode),
        "stdout": str(stdout or ""),
        "stderr": str(stderr or ""),
        "timed_out": bool(timed_out),
        "status": normalized_status,
    }


__all__ = [
    "default_audit_path",
    "read_audit_entries",
    "summarize_audit_entries",
    "append_audit_entry",
    "build_audit_entry",
]

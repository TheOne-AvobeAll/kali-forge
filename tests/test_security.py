from pathlib import Path

import pytest

from kali_forge.security import ensure_within_directory, validate_allowed_executable


def test_ensure_within_directory_allows_nested_paths() -> None:
    base = Path("/tmp/kali-forge")
    child = base / "workspace" / "notes.txt"
    assert ensure_within_directory(child, base) == child.resolve(strict=False)


def test_ensure_within_directory_rejects_traversal() -> None:
    base = Path("/tmp/kali-forge")
    with pytest.raises(ValueError):
        ensure_within_directory("/tmp/../etc/passwd", base)


def test_validate_allowed_executable_rejects_untrusted_command() -> None:
    with pytest.raises(ValueError):
        validate_allowed_executable("rm", allowed_commands={"echo", "python"})


def test_validate_allowed_executable_accepts_allowlisted_command() -> None:
    executable = validate_allowed_executable("python", allowed_commands={"echo", "python"})
    assert executable.name == "python"

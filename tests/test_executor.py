from kali_forge.config import AppConfig
from kali_forge.executor import CommandRunner


def test_runner_executes_allowlisted_command() -> None:
    runner = CommandRunner(AppConfig())
    result = runner.run(["echo", "hello"])
    assert result.returncode == 0
    assert result.stdout.strip() == "hello"
    assert result.timed_out is False


def test_runner_rejects_unapproved_command() -> None:
    runner = CommandRunner(AppConfig(allowed_commands=("echo",)))
    try:
        runner.run(["python", "-c", "print('nope')"])
    except Exception as exc:  # pragma: no cover - defensive API contract
        assert "not in the configured allowlist" in str(exc)
    else:
        raise AssertionError("Expected a ValueError for unapproved command execution.")

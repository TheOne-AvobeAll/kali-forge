from kali_forge.lab import LabConfig, load_lab_config, save_default_lab_config


def test_lab_config_defaults_are_valid() -> None:
    config = LabConfig()
    assert config.name == "default-lab"
    assert config.allowed_commands
    assert config.timeout_seconds > 0


def test_lab_config_save_and_load_round_trip(tmp_path) -> None:
    target = tmp_path / "lab.json"
    saved = save_default_lab_config(target)
    loaded = load_lab_config(target)
    assert saved.name == loaded.name
    assert saved.allowed_commands == loaded.allowed_commands
    assert saved.workdir == loaded.workdir


def test_lab_config_rejects_empty_name() -> None:
    try:
        LabConfig(name=" ")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty lab name.")

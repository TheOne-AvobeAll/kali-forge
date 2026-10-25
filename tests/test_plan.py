from kali_forge.plan import ExecutionPlan, PlanStep, load_plan, save_default_plan


def test_execution_plan_defaults_are_valid() -> None:
    plan = ExecutionPlan()
    assert plan.name == "default-plan"
    assert len(plan.steps) >= 2


def test_plan_save_and_load_round_trip(tmp_path) -> None:
    target = tmp_path / "plan.json"
    saved = save_default_plan(target)
    loaded = load_plan(target)
    assert saved.name == loaded.name
    assert saved.steps[0].command == loaded.steps[0].command


def test_plan_step_rejects_empty_command() -> None:
    try:
        PlanStep(name="demo", command=" ")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty plan step command.")

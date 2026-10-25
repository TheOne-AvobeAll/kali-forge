from kali_forge.workflow import WorkflowSpec, get_workflow, list_workflows, parse_command_step


def test_list_workflows_returns_builtin_entries() -> None:
    workflows = list_workflows()
    assert {workflow.name for workflow in workflows} == {"hello-world", "list-env"}


def test_get_workflow_returns_expected_definition() -> None:
    workflow = get_workflow("hello-world")
    assert workflow.name == "hello-world"
    assert workflow.steps[0] == "echo 'hello from kali-forge'"


def test_parse_command_step_handles_quotes() -> None:
    parsed = parse_command_step("python -c \"print('x')\"")
    assert parsed[0] == "python"
    assert parsed[1] == "-c"
    assert parsed[2] == "print('x')"


def test_workflow_rejects_empty_name() -> None:
    try:
        WorkflowSpec(name=" ", description="desc", steps=("echo hi",))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty workflow name.")

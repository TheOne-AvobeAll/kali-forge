from kali_forge.workflow import WorkflowSpec, get_workflow, list_workflows


def test_list_workflows_returns_builtin_entries() -> None:
    workflows = list_workflows()
    assert {workflow.name for workflow in workflows} == {"hello-world", "list-env"}


def test_get_workflow_returns_expected_definition() -> None:
    workflow = get_workflow("hello-world")
    assert workflow.name == "hello-world"
    assert workflow.steps[0] == "echo hello from kali-forge"


def test_workflow_rejects_empty_name() -> None:
    try:
        WorkflowSpec(name=" ", description="desc", steps=("echo hi",))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty workflow name.")


def test_workflow_rejects_empty_steps() -> None:
    try:
        WorkflowSpec(name="demo", description="desc", steps=())
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty workflow steps.")

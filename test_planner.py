from app.brain.planner import create_architecture_plan
from app.project.inspector import inspect_project
from app.project.environment import inspect_environment


PROJECT_ROOT = "/workspaces/spongebob-ai"


def test_planner_functions_are_available():
    assert callable(create_architecture_plan)
    assert callable(inspect_project)
    assert callable(inspect_environment)


def test_project_inspection():
    project_context = inspect_project(PROJECT_ROOT)

    assert project_context is not None


def test_environment_inspection():
    environment_context = inspect_environment()

    assert environment_context is not None

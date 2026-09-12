import json

from app.brain.planner import create_architecture_plan
from app.project.inspector import inspect_project
from app.project.environment import inspect_environment


PROJECT_ROOT = r"C:\Users\sreek\SpongeBob AI"


project_context = inspect_project(PROJECT_ROOT)
environment_context = inspect_environment()


plan = create_architecture_plan(
    goal="Build a portfolio website",
    project_type="portfolio",
    requirements={
        "project_type": "portfolio",
        "core_pages": [
            "Home",
            "About",
            "Projects",
            "Contact",
        ],
        "placeholder_content_strategy": (
            "to be used for missing user-specific assets"
        ),
    },
    user_facts={},
    delegated_decisions=[],
    inferences={
        "portfolio_pages": [
            "Home",
            "About",
            "Projects/Work",
            "Contact",
        ],
        "tech_stack_flexibility": True,
        "placeholder_content_acceptable": True,
    },
    project_context=project_context,
    environment_context=environment_context,
)


print(json.dumps(plan, indent=2))
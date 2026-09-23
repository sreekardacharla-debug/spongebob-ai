from app.agent import implementation


def test_implementation_prompt_uses_project_and_environment_context(monkeypatch):
    captured = {}

    def fake_generate(prompt):
        captured["prompt"] = prompt
        return '{"operations": []}'

    monkeypatch.setattr(
        implementation.model_service,
        "generate",
        fake_generate,
    )

    architecture_plan = {
        "architecture_summary": "Use the existing Vite frontend.",
        "frontend": {
            "needed": True,
            "technology": "Vite + React",
        },
    }

    project_context = {
        "root": "/workspace",
        "detected_project_types": [
            "javascript_or_node",
            "vite",
        ],
        "files": [
            "package.json",
            "src/App.jsx",
        ],
    }

    environment_context = {
        "operating_system": "Linux",
        "tools": {
            "node": "v22.0.0",
            "npm": "10.0.0",
        },
    }

    result = implementation.create_implementation_plan(
        architecture_plan=architecture_plan,
        project_context=project_context,
        environment_context=environment_context,
    )

    assert result == {"operations": []}

    prompt = captured["prompt"]

    assert "Use the existing Vite frontend." in prompt
    assert "javascript_or_node" in prompt
    assert "src/App.jsx" in prompt
    assert "v22.0.0" in prompt
    assert "npm" in prompt


def test_implementation_prompt_protects_existing_project():
    prompt = implementation._build_prompt(
        architecture_plan={
            "architecture_summary": "Add a dashboard feature."
        },
        project_context={
            "detected_project_types": ["vite", "javascript_or_node"],
            "files": ["package.json", "src/App.jsx"],
        },
        environment_context={
            "tools": {
                "node": "v22.0.0",
                "npm": "10.0.0",
            }
        },
    )

    assert "Prefer extending the existing project" in prompt
    assert "Do not recreate an existing file as create_file" in prompt
    assert "Modify the smallest reasonable set" in prompt
    assert "Do not rewrite unrelated files" in prompt
    assert "Do not introduce new dependencies unless they are required" in prompt
    assert "Do not assume a runtime, package manager" in prompt
    assert "Do not silently rebuild the entire project" in prompt

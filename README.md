# SpongeBob AI

SpongeBob AI is a cloud-first autonomous software-engineering assistant focused on understanding natural-language goals, inspecting projects, planning changes, executing controlled filesystem operations, validating results, and recovering through Last-Known-Good snapshots.

## Architecture

- **Model layer:** provider abstraction with Qwen through Amazon Bedrock; routing can be extended to additional providers.
- **Security layer:** identity, policy engine, capabilities, protected resources, and a model gateway that keeps raw credentials outside the model.
- **Brain:** request understanding, progressive requirements analysis, decision history, architecture planning.
- **Project awareness:** project and environment inspection before planning.
- **Agent loop:** LangGraph orchestration for planning, implementation, validation, diagnosis, repair, restore, and snapshot promotion.
- **Workspace safety:** project-bound filesystem operations and controlled terminal execution.
- **Recovery:** Last-Known-Good snapshots before implementation changes.
- **CLI:** terminal-first user interface with persistent LangGraph thread state.

## Run

After authenticating AWS in the environment:

```bash
python -m app.main
```

Or:

```bash
python main.py
```

## Verify

Run the complete verification suite:

```bash
python scripts/verify_all.py
```

The verifier checks the Python test suite, imports, security policy, filesystem isolation, snapshot recovery, decision history, LangGraph structure, CLI wiring, AWS authentication, and a live Qwen → Bedrock request.

## AWS

SpongeBob uses the AWS credential chain available to the runtime. Do not put access keys, session tokens, SSO tokens, or other secrets in source code or send them through the model.

For an expired AWS session, refresh the AWS login in the runtime and run the verifier again.

## Current scope

The project is intentionally being built in layers. Snowflake persistence, richer audit logging, production authentication, stronger terminal sandboxing, and additional model providers are extension points rather than claims that the current local prototype already provides those production guarantees.

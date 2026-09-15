from app.llm.claude import ClaudeProvider


claude = ClaudeProvider()

response = claude.generate(
    "You are SpongeBob AI. Reply with one short sentence confirming that Claude is connected."
)

print("Claude response:")
print(response)

from app.llm.router import ModelRouter


router = ModelRouter()

response = router.generate(
    "Reply with exactly: SpongeBob router is working."
)

print("Router response:")
print(response)

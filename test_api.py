from huggingface_hub import InferenceClient

# Replace with your actual API key
HUGGING_FACE_API_KEY = "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"# Replace with your actual key from huggingface.co

# Models to try (in order)
models_to_try = [
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "HuggingFaceH4/zephyr-7b-beta",
    "google/gemma-7b-it",
    "microsoft/Phi-3-mini-4k-instruct"
]

client = InferenceClient(token=API_KEY)

print("Testing models...\n")

for model in models_to_try:
    try:
        print(f"Trying: {model}")
        response = client.chat_completion(
            messages=[{"role": "user", "content": "Say hello!"}],
            model=model,
            max_tokens=50
        )
        
        print(f"✅ SUCCESS with {model}")
        print(f"Response: {response.choices[0].message.content}\n")
        print(f"👉 USE THIS MODEL: {model}")
        break
        
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}...\n")
        continue

print("\nIf none worked, you may need to enable API access for these models on Hugging Face")
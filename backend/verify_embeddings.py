
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from embedding_service import generate_embedding
from config import get_settings

def verify():
    settings = get_settings()
    print(f"Checking configuration...")
    print(f"Model: {settings.embedding_model}")
    print(f"Base URL: {settings.embedding_base_url}")
    
    if not settings.github_token:
        print("ERROR: GITHUB_TOKEN is not set in environment or .env file.")
        print("Please set GITHUB_TOKEN to run this verification.")
        return

    print(f"Token present (len={len(settings.github_token)})")
    
    test_text = "Inventix AI is a deterministic similarity engine."
    print(f"\nGenerating embedding for: '{test_text}'")
    
    result = generate_embedding(test_text)
    
    if result.success:
        print("\nSUCCESS!")
        print(f"Dimensions: {len(result.embedding)}")
        print(f"First 5 values: {result.embedding[:5]}")
        print(f"Model used: {result.model_name}")
    else:
        print("\nFAILED.")
        print(f"Error: {result.error}")

if __name__ == "__main__":
    verify()

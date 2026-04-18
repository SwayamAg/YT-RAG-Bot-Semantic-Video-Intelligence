import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

def test_azure_config():
    print("="*50)
    print("   AZURE OPENAI DIAGNOSTIC TOOL")
    print("="*50)
    
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    # LLM Config
    llm_key = os.getenv("AZURE_OPENAI_API_KEY")
    llm_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    llm_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    # Embeddings Config
    embed_key = os.getenv("AZURE_EMBEDDINGS_API_KEY") or llm_key
    embed_endpoint = os.getenv("AZURE_EMBEDDINGS_ENDPOINT") or llm_endpoint
    embed_deployment = os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT")

    # 1. Test LLM Deployment
    print(f"\n[1/2] Testing LLM Deployment: '{llm_deployment}'...")
    try:
        client_llm = AzureOpenAI(
            api_key=llm_key,
            api_version=api_version,
            azure_endpoint=llm_endpoint
        )
        response = client_llm.chat.completions.create(
            model=llm_deployment,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print("OK: LLM Connection Successful!")
    except Exception as e:
        print(f"ERROR: LLM Error: {e}")

    # 2. Test Embeddings Deployment
    print(f"\n[2/2] Testing Embeddings Deployment: '{embed_deployment}'...")
    print(f"      Endpoint: {embed_endpoint}")
    try:
        client_embed = AzureOpenAI(
            api_key=embed_key,
            api_version=api_version,
            azure_endpoint=embed_endpoint
        )
        response = client_embed.embeddings.create(
            model=embed_deployment,
            input="Test embedding"
        )
        print("OK: Embeddings Connection Successful!")
    except Exception as e:
        print(f"ERROR: Embeddings Error: {e}")
        if "401" in str(e) or "Unauthorized" in str(e):
            print("   TIP: Since this is a different endpoint, you likely need a DIFFERENT API Key.")
            print("   Update line 8 of your .env with the key for the 'e23cs' resource.")

if __name__ == "__main__":
    test_azure_config()

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

def find_embedding_deployment():
    print("="*50)
    print("   DISCOVERY: AZURE OPENAI DEPLOYMENTS")
    print("="*50)
    
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )

    # Expanded list of common names
    common_names = [
        "text-embedding-3-small",
        "text-embedding-ada-002",
        "rag-lab-embeddings",
        "embeddings",
        "embedding-deployment",
        "text-embedding-3-large",
        "embedding-model"
    ]

    print("[*] Testing common embedding deployment names...")
    
    found = False
    for name in common_names:
        print(f"    - Trying '{name}'...", end=" ", flush=True)
        try:
            client.embeddings.create(
                model=name,
                input="test"
            )
            print("FOUND!")
            print(f"\n[SUCCESS] Working deployment: '{name}'")
            print(f"Update your .env to: AZURE_EMBEDDINGS_DEPLOYMENT={name}")
            found = True
            break
        except Exception as e:
            # Check if it's a 404 or something else
            if "404" in str(e):
                print("Not Found (404)")
            else:
                print(f"Error: {str(e)[:50]}...")

    if not found:
        print("\n[!] No common names worked.")
        print("Please check your Azure AI Studio -> Deployments tab.")

if __name__ == "__main__":
    find_embedding_deployment()

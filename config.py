import os
import sys
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from utils import extract_video_id

# Load environment variables
load_dotenv()

# --- Project Constants ---
_raw_url_or_id = os.getenv("YOUTUBE_URL") or os.getenv("YOUTUBE_VIDEO_ID", "Gfr50f6ZBvo")
YOUTUBE_VIDEO_ID = extract_video_id(_raw_url_or_id)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
FAISS_INDEX_PATH = "faiss_index"
LOCAL_TRANSCRIPT_PATH = "transcript.txt"

# Retriever settings
RETRIEVAL_K = 4
SEARCH_TYPE = "similarity"

def validate_env():
    """Validates that all necessary Azure OpenAI environment variables are set."""
    required = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_EMBEDDINGS_DEPLOYMENT"
    ]
    missing = [var for var in required if not os.getenv(var)]
    if missing:
        print(f"[ERROR] Missing environment variables: {', '.join(missing)}")
        print("Please check your .env file.")
        return False
    return True

def get_llm():
    """Initializes and returns the Azure OpenAI Chat model."""
    if not validate_env():
        sys.exit(1)
        
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        temperature=0.2
    )

def get_embeddings():
    """Initializes and returns the Azure OpenAI Embeddings model."""
    if not validate_env():
        sys.exit(1)
        
    # Support for separate embedding resource (Endpoint and Key)
    endpoint = os.getenv("AZURE_EMBEDDINGS_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_EMBEDDINGS_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    
    return AzureOpenAIEmbeddings(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT"),
    )

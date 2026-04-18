import os
from typing import Optional
from langchain_community.document_loaders import YoutubeLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from config import (
    CHUNK_SIZE, 
    CHUNK_OVERLAP, 
    FAISS_INDEX_PATH, 
    LOCAL_TRANSCRIPT_PATH,
    get_embeddings
)

def fetch_transcript_from_youtube(video_id: str) -> Optional[str]:
    """Attempts to fetch transcript from YouTube using LangChain's YoutubeLoader."""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"[FETCH] Attempting to download transcript from: {url}")
        loader = YoutubeLoader.from_youtube_url(url, add_video_info=False)
        docs = loader.load()
        if docs:
            print("[SUCCESS] Transcript successfully downloaded from YouTube.")
            return docs[0].page_content
        return None
    except Exception as e:
        print(f"[WARNING] YouTube download failed: {e}")
        return None

def fetch_transcript_from_local() -> Optional[str]:
    """Attempts to fetch transcript from a local fallback file."""
    if os.path.exists(LOCAL_TRANSCRIPT_PATH):
        try:
            print(f"[FETCH] Using local fallback file: {LOCAL_TRANSCRIPT_PATH}")
            loader = TextLoader(LOCAL_TRANSCRIPT_PATH, encoding='utf-8')
            docs = loader.load()
            return docs[0].page_content
        except Exception as e:
            print(f"[ERROR] Local fallback failed: {e}")
    return None

def get_or_create_vector_store(video_id: str):
    """Manages the Vector Store lifecycle for a specific video_id."""
    embeddings = get_embeddings()
    
    # Use a unique index path per video if possible, or just the default
    # For simplicity, we'll keep one index, but we could make it video-specific:
    # index_path = f"faiss_index_{video_id}"
    index_path = FAISS_INDEX_PATH
    
    # Check if a persistent index exists on disk
    if os.path.exists(index_path):
        print(f"[INDEX] Loading existing FAISS index from '{index_path}'...")
        try:
            return FAISS.load_local(
                index_path, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"[RECOVERY] Local index corrupted or incompatible: {e}. Re-indexing...")

    # Data Ingestion Pipeline
    print(f"[INDEX] Initializing ingestion pipeline for Video ID: {video_id}...")
    transcript = fetch_transcript_from_youtube(video_id)
    
    if not transcript:
        transcript = fetch_transcript_from_local()
        
    if not transcript:
        print(f"[CRITICAL] No data found! Provide a '{LOCAL_TRANSCRIPT_PATH}' file to proceed.")
        return None
        
    # Semantic Chunking
    print(f"[PROCESS] Splitting text into chunks (Size={CHUNK_SIZE}, Overlap={CHUNK_OVERLAP})...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.create_documents([transcript])
    print(f"[PROCESS] Generated {len(chunks)} document segments.")
    
    # Vectorization
    print("[INDEX] Generating embeddings and building FAISS index...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Persistence
    vector_store.save_local(index_path)
    print(f"[INDEX] FAISS index persisted locally at '{index_path}'.")
    
    return vector_store

if __name__ == "__main__":
    from config import YOUTUBE_VIDEO_ID
    if get_or_create_vector_store(YOUTUBE_VIDEO_ID):
        print("[OK] Ingestion system diagnostic passed.")

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

def fetch_transcript_with_ytdlp(video_id: str) -> Optional[str]:
    """Uses yt-dlp to extract transcripts. Highly robust against blocks."""
    import yt_dlp
    import requests
    import json
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"[FETCH] Attempting pro-fetch with yt-dlp for: {video_id}")
    
    ydl_opts = {
        'skip_download': True,
        'writeautomaticsub': True,
        'writesubtitles': True,
        'subtitleslangs': ['en.*', 'hi.*'], # Support English and Hindi
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Prioritize manual subtitles over automatic ones
            subtitles = info.get('subtitles') or info.get('automatic_captions')
            if not subtitles:
                return None
                
            # Pick the first available English/Hindi subtitle
            for lang in ['en', 'en-US', 'hi']:
                for key in subtitles.keys():
                    if key.startswith(lang):
                        # Get the JSON format URL if available, else VTT
                        formats = subtitles[key]
                        json_fmt = next((f['url'] for f in formats if f.get('ext') == 'json3'), None)
                        if json_fmt:
                            resp = requests.get(json_fmt)
                            if resp.status_code == 200:
                                data = resp.json()
                                formatted_events = []
                                for event in data.get('events', []):
                                    if 'segs' in event and 'tStartMs' in event:
                                        # Convert ms to M:SS or H:MM:SS
                                        ms = event['tStartMs']
                                        s = ms // 1000
                                        m, s = divmod(s, 60)
                                        h, m = divmod(m, 60)
                                        time_str = f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
                                        
                                        text = "".join([seg['utf8'] for seg in event['segs'] if 'utf8' in seg])
                                        formatted_events.append(f"[{time_str}] {text}")
                                
                                return " ".join(formatted_events)
        return None
    except Exception as e:
        print(f"[WARNING] yt-dlp extraction failed: {e}")
        return None

def fetch_transcript_from_youtube(video_id: str) -> Optional[str]:
    """
    Advanced fetcher that prioritizes yt-dlp for robustness.
    """
    # 1. Try yt-dlp (Pro)
    transcript = fetch_transcript_with_ytdlp(video_id)
    if transcript:
        print("[SUCCESS] Transcript fetched via yt-dlp.")
        return transcript

    # 2. Fallback to youtube-transcript-api (Fast)
    from youtube_transcript_api import YouTubeTranscriptApi
    try:
        print(f"[FETCH] Falling back to standard scraper for: {video_id}")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript_obj = transcript_list.find_transcript(['en', 'hi'])
        except:
            transcript_obj = next(iter(transcript_list))
            
        data = transcript_obj.fetch()
        return " ".join([t['text'] for t in data])
        
    except Exception as e:
        print(f"\033[91m[NOTICE]\033[0m Live transcript not fetchable for this video.")
        print(f"         Reason: {str(e)[:100]}...")
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
    is_fallback = False
    
    # Use unique index path per video to avoid loading old data from other videos
    index_path = os.path.join(FAISS_INDEX_PATH, video_id)
    fallback_index_path = os.path.join(FAISS_INDEX_PATH, "local_fallback")
    
    # 1. Check if a persistent index for THIS video exists on disk
    if os.path.exists(index_path):
        print(f"[INDEX] Loading existing FAISS index for Video ID: {video_id}...")
        try:
            return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True), False
        except Exception as e:
            print(f"[RECOVERY] Local index corrupted: {e}. Re-indexing...")

    # 2. Try to fetch and index NEW transcript
    print(f"[INDEX] Initializing ingestion pipeline for Video ID: {video_id}...")
    transcript = fetch_transcript_from_youtube(video_id)
    
    # 3. Handle Fallback if fetch fails
    if not transcript:
        print(f"\033[93m[FALLBACK]\033[0m Transcript fetch failed. Shifting to default local transcript...")
        is_fallback = True
        # Check if we already have a saved index for the fallback file
        if os.path.exists(fallback_index_path):
             return FAISS.load_local(fallback_index_path, embeddings, allow_dangerous_deserialization=True), True
        transcript = fetch_transcript_from_local()
        save_path = fallback_index_path
    else:
        save_path = index_path
        
    if not transcript:
        print(f"\n\033[91m[CRITICAL]\033[0m No data found! Provide a '{LOCAL_TRANSCRIPT_PATH}' file to proceed.")
        return None, False
        
    # Semantic Chunking & Vectorization
    print(f"[PROCESS] Splitting text into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.create_documents([transcript])
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    # Persistence
    vector_store.save_local(save_path)
    print(f"[INDEX] Index persisted at '{save_path}'.")
    
    return vector_store, is_fallback

if __name__ == "__main__":
    from config import YOUTUBE_VIDEO_ID
    if get_or_create_vector_store(YOUTUBE_VIDEO_ID):
        print("[OK] Ingestion system diagnostic passed.")

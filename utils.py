import re
from typing import Optional
from langchain_community.document_loaders import YoutubeLoader

def extract_video_id(url: str) -> Optional[str]:
    """
    Extracts the YouTube video ID from various URL formats.
    """
    if not url:
        return None
        
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})'
    
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    
    if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
        
    return None

def get_video_title(video_id: str) -> str:
    """
    Fetches the title of a YouTube video using its ID.
    """
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
        docs = loader.load()
        if docs and "title" in docs[0].metadata:
            return docs[0].metadata["title"]
        return "Unknown Video"
    except Exception:
        return "Unknown Video"

if __name__ == "__main__":
    # Test cases
    urls = ["https://www.youtube.com/watch?v=Gfr50f6ZBvo"]
    for u in urls:
        vid = extract_video_id(u)
        print(f"ID: {vid} -> Title: {get_video_title(vid)}")

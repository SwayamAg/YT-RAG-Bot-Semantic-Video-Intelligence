import os
import sys
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from utils import extract_video_id, get_video_title
from config import LOCAL_TRANSCRIPT_PATH, YOUTUBE_VIDEO_ID

# ANSI Colors for terminal
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def test_youtube_ingestion(target_url=None):
    # 1. Resolve Target
    raw_input = target_url or os.getenv("YOUTUBE_URL") or YOUTUBE_VIDEO_ID
    video_id = extract_video_id(raw_input)
    
    print(f"\n{BOLD}[1/3] Video Identification{RESET}")
    if not video_id:
        print(f"      {RED}ERROR: Could not extract Video ID from: {raw_input}{RESET}")
        video_id = "INVALID"
    else:
        title = get_video_title(video_id)
        print(f"      Target URL: {raw_input}")
        print(f"      Video ID:   {YELLOW}{video_id}{RESET}")
        print(f"      Title:      {YELLOW}{title}{RESET}")
        print(f"      {GREEN}OK: Video identified.{RESET}")

    # 2. Test Transcript API (Current Scraper)
    print(f"\n{BOLD}[2/4] Testing Standard Scraper (youtube-transcript-api){RESET}")
    if video_id == "INVALID":
        print(f"      {RED}SKIPPED: Cannot fetch transcript for invalid ID.{RESET}")
    else:
        try:
            print(f"      Attempting to fetch transcript for {video_id}...")
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            char_count = sum(len(t['text']) for t in transcript_list)
            print(f"      {GREEN}SUCCESS: Transcript found!{RESET}")
            print(f"      Stats: {len(transcript_list)} segments, ~{char_count} characters.")
        except Exception as e:
            print(f"      {RED}FAILED: {type(e).__name__}{RESET}")
            print(f"      Details: {str(e)[:100]}...")

    # 3. Test yt-dlp (Pro Scraper)
    print(f"\n{BOLD}[3/4] Testing Pro Scraper (yt-dlp){RESET}")
    if video_id == "INVALID":
         print(f"      {RED}SKIPPED.{RESET}")
    else:
        try:
            import yt_dlp
            print(f"      Attempting to extract subtitles with yt-dlp...")
            ydl_opts = {
                'skip_download': True,
                'writeautomaticsub': True,
                'writesubtitles': True,
                'subtitleslangs': ['en.*'],
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                # Check if subtitles were found in the info dict
                if 'subtitles' in info and info['subtitles']:
                    print(f"      {GREEN}SUCCESS: Manual subtitles found.{RESET}")
                elif 'automatic_captions' in info and info['automatic_captions']:
                    print(f"      {GREEN}SUCCESS: Automatic captions found.{RESET}")
                else:
                    print(f"      {RED}FAILED: No subtitles found via yt-dlp.{RESET}")
        except Exception as e:
            print(f"      {RED}FAILED: Error during yt-dlp extraction: {e}{RESET}")

    # 4. Test Local Fallback
    print(f"\n{BOLD}[4/4] Checking Local Fallback System{RESET}")
    if os.path.exists(LOCAL_TRANSCRIPT_PATH):
        try:
            with open(LOCAL_TRANSCRIPT_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
                preview = content[:100].replace('\n', ' ')
                print(f"      Path: {YELLOW}{LOCAL_TRANSCRIPT_PATH}{RESET}")
                print(f"      Status: {GREEN}File Found{RESET}")
                print(f"      Size: {len(content)} characters")
                print(f"      Preview: \"{preview}...\"")
        except Exception as e:
            print(f"      {RED}ERROR: Found file but could not read it: {e}{RESET}")
    else:
        print(f"      Path: {LOCAL_TRANSCRIPT_PATH}")
        print(f"      Status: {YELLOW}Not Found{RESET}")
        print(f"      {CYAN}TIP: Create this file to use the bot when YouTube scrapers are blocked.{RESET}")

    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"   DIAGNOSTIC COMPLETE")
    print(f"{CYAN}{'='*60}{RESET}\n")

if __name__ == "__main__":
    # Clear screen for better visibility
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f"{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}   YOUTUBE TRANSCRIPT DIAGNOSTIC TOOL{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")

    # Prompt for input
    print(f"\n{BOLD}Paste a YouTube URL or Video ID below.{RESET}")
    target = input(f"{YELLOW}Input (press Enter for default): {RESET}").strip()
    
    test_youtube_ingestion(target or None)

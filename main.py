import sys
import os
from rag_chain import get_rag_chain
from config import LOCAL_TRANSCRIPT_PATH, YOUTUBE_VIDEO_ID
from utils import extract_video_id, get_video_title

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("\033[96m" + "="*50)
    print("   📺 YOUTUBE TRANSCRIPT RAG - SMART CHAT")
    print("="*50 + "\033[0m")
    
    # 1. Fetch Default Info
    default_id = YOUTUBE_VIDEO_ID
    print("[*] Checking default video info...")
    default_title = get_video_title(default_id)
    
    # 2. Dynamic Video Selection Prompt
    print(f"\nDefault Video: \033[95m{default_title}\033[0m")
    print(f"Default ID: \033[90m{default_id}\033[0m")
    
    target_input = input("\n\033[1m\033[93mEnter YouTube URL or ID (press Enter for default): \033[0m").strip()
    
    if not target_input:
        vid_id = default_id
        vid_title = default_title
    else:
        vid_id = extract_video_id(target_input)
        if not vid_id:
            print("\033[91m[ERROR]\033[0m Invalid YouTube URL or ID format.")
            sys.exit(1)
        print("[*] Fetching video title...")
        vid_title = get_video_title(vid_id)
    
    clear_screen()
    print("\033[96m" + "="*50)
    print("   📺 YOUTUBE TRANSCRIPT RAG - SMART CHAT")
    print("="*50 + "\033[0m")
    print(f"Target Video: \033[95m{vid_title}\033[0m")
    print(f"Target ID: \033[90m{vid_id}\033[0m\n")
    print("Commands: 'exit' to quit, 'clear' to reset terminal\n")
    
    try:
        print("[*] Initializing RAG Logic and Vector Index...")
        rag_chain = get_rag_chain(vid_id)
        
        if not rag_chain:
            print("\n\033[91m[FAILED]\033[0m Initialization aborted.")
            print(f"Suggestion: Check .env or add transcript to '{LOCAL_TRANSCRIPT_PATH}'.")
            sys.exit(1)
            
        print("\033[92m[READY]\033[0m Ask me anything about the video content!\n")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        sys.exit(1)
    
    while True:
        try:
            user_input = input("\033[1m\033[94mYou >> \033[0m").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                print("\033[93mShutting down. Goodbye!\033[0m")
                break
                
            if user_input.lower() == "clear":
                clear_screen()
                print(f"Target Video: \033[95m{vid_title}\033[0m")
                print(f"Target ID: \033[90m{vid_id}\033[0m\n")
                continue
            
            # Chain execution
            print("\033[90mThinking...\033[0m", end="\r")
            response = rag_chain.invoke(user_input)
            
            # Display response
            print("\r" + " " * 15, end="\r") # Clear 'Thinking...'
            print(f"\033[95mAssistant:\033[0m {response}\n")
            
        except KeyboardInterrupt:
            print("\n\033[93mTerminated by user.\033[0m")
            break
        except Exception as e:
            print(f"\n\033[91m[ERROR]\033[0m {e}")

if __name__ == "__main__":
    main()

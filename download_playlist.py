#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Playlist MP3 Downloader - Interactive Mode
Tải nhạc MP3 từ playlist YouTube (chế độ tương tác)

Author: Your Name
License: MIT
"""

import os
import sys
import subprocess
from pathlib import Path

# Fix encoding cho Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def check_dependencies():
    """Kiểm tra và cài đặt dependencies"""
    try:
        import yt_dlp
        print("[OK] yt-dlp installed")
        return True
    except ImportError:
        print("[*] Installing yt-dlp...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"])
        print("[OK] yt-dlp installed")
        return True


def download_playlist(playlist_url: str, output_folder: str = None, quality: str = "192"):
    """
    Tải playlist YouTube thành MP3
    
    Args:
        playlist_url: URL playlist YouTube
        output_folder: Thư mục lưu file (mặc định: ./downloads)
        quality: Chất lượng MP3 (128, 192, 256, 320)
    """
    import yt_dlp
    
    script_dir = Path(__file__).parent.absolute()
    
    if output_folder is None:
        output_folder = script_dir / "downloads"
    else:
        output_folder = Path(output_folder)
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[FOLDER] {output_folder}")
    print(f"[URL] {playlist_url}")
    print(f"[QUALITY] {quality}kbps")
    print("-" * 60)
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            print(f"\r    >> {percent} | {speed}    ", end='', flush=True)
        elif d['status'] == 'finished':
            filename = Path(d.get('filename', '')).name
            print(f"\n[OK] {filename}")
    
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'outtmpl': str(output_folder / '%(playlist_index)04d - %(title)s.%(ext)s'),
        'ffmpeg_location': str(script_dir),
        'ignoreerrors': True,
        'nooverwrites': True,
        'no_warnings': True,
        'retries': 3,
        'geo_bypass': True,
        'progress_hooks': [progress_hook],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\n[INFO] Getting playlist info...")
            info = ydl.extract_info(playlist_url, download=False)
            
            if 'entries' in info:
                total = len([e for e in info['entries'] if e])
                print(f"[FOUND] {total} videos")
                print("-" * 60)
            
            print("\n[START] Downloading...\n")
            ydl.download([playlist_url])
        
        print("\n" + "=" * 60)
        print("[DONE] Completed!")
        print(f"[FOLDER] {output_folder}")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


def main():
    """Entry point - Interactive mode"""
    print("=" * 60)
    print("   YOUTUBE PLAYLIST MP3 DOWNLOADER")
    print("   Interactive Mode")
    print("=" * 60)
    
    check_dependencies()
    
    # URL mặc định
    default_url = "https://youtube.com/playlist?list=PL9dppUWWRkOfdciwdVkEBioMRixdqgjPz"
    
    print(f"\n[INPUT] Enter YouTube playlist URL")
    print(f"        (Press Enter for default)")
    url = input("[URL] ").strip() or default_url
    
    print("\n[INPUT] Enter output folder (Press Enter for 'downloads'):")
    folder = input("[FOLDER] ").strip() or None
    
    print("\n[INPUT] Enter MP3 quality (128/192/256/320, default: 192):")
    quality = input("[QUALITY] ").strip() or "192"
    
    download_playlist(url, folder, quality)
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()

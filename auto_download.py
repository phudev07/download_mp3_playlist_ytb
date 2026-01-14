#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Playlist MP3 Downloader - Fast Mode
Tải nhạc MP3 từ playlist YouTube với đa luồng song song

Author: Your Name
License: MIT
"""

import os
import sys
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Fix encoding cho Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ==================== CẤU HÌNH ====================
# URL playlist YouTube cần tải
PLAYLIST_URL = "https://youtube.com/playlist?list=PL9dppUWWRkOfdciwdVkEBioMRixdqgjPz"

# Thư mục lưu file MP3 (None = thư mục "downloads" trong folder script)
OUTPUT_FOLDER = None

# Chất lượng MP3: "128", "192", "256", "320"
MP3_QUALITY = "192"

# Số luồng tải song song (tăng lên nếu mạng mạnh)
MAX_WORKERS = 30
# ==================================================


class PlaylistDownloader:
    """Class quản lý việc tải playlist YouTube"""
    
    def __init__(self, playlist_url: str, output_folder: str = None, 
                 quality: str = "192", max_workers: int = 5):
        self.playlist_url = playlist_url
        self.quality = quality
        self.max_workers = max_workers
        
        # Xác định thư mục
        self.script_dir = Path(__file__).parent.absolute()
        self.output_folder = Path(output_folder) if output_folder else self.script_dir / "downloads"
        self.ffmpeg_path = self.script_dir / "ffmpeg.exe"
        
        # Counters thread-safe
        self._download_count = 0
        self._lock = threading.Lock()
        self.total_videos = 0
    
    def _check_dependencies(self) -> bool:
        """Kiểm tra và cài đặt dependencies"""
        # Kiểm tra yt-dlp
        try:
            import yt_dlp
            print("[OK] yt-dlp installed")
        except ImportError:
            print("[*] Installing yt-dlp...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"])
            print("[OK] yt-dlp installed")
        
        # Kiểm tra FFmpeg
        if not self.ffmpeg_path.exists():
            # Thử tìm trong PATH
            try:
                subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
                print("[OK] FFmpeg found in PATH")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"[ERROR] FFmpeg not found!")
                print(f"        Expected at: {self.ffmpeg_path}")
                print("        Download from: https://ffmpeg.org/download.html")
                return False
        
        print(f"[OK] FFmpeg: {self.ffmpeg_path}")
        return True
    
    def _increment_counter(self) -> int:
        """Thread-safe counter increment"""
        with self._lock:
            self._download_count += 1
            return self._download_count
    
    def _download_single(self, video_info: dict, index: int) -> tuple:
        """Tải một video thành MP3"""
        import yt_dlp
        
        video_url = video_info.get('url') or video_info.get('webpage_url')
        title = video_info.get('title', 'Unknown')[:60]
        
        if not video_url:
            return False, f"No URL: {title}"
        
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.quality,
            }],
            'outtmpl': str(self.output_folder / f'{index:03d} - %(title)s.%(ext)s'),
            'ffmpeg_location': str(self.script_dir),
            'ignoreerrors': True,
            'nooverwrites': True,
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'geo_bypass': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            count = self._increment_counter()
            print(f"[{count}/{self.total_videos}] {title}")
            return True, title
            
        except Exception as e:
            print(f"[ERROR] {title}: {str(e)[:50]}")
            return False, str(e)
    
    def _get_playlist_videos(self) -> list:
        """Lấy danh sách video từ playlist"""
        import yt_dlp
        
        ydl_opts = {
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.playlist_url, download=False)
        
        if 'entries' not in info:
            return []
        
        return [v for v in info['entries'] if v]
    
    def download(self) -> bool:
        """Tải toàn bộ playlist"""
        # Header
        print("=" * 60)
        print("   YOUTUBE PLAYLIST MP3 DOWNLOADER")
        print(f"   Threads: {self.max_workers} | Quality: {self.quality}kbps")
        print("=" * 60)
        
        # Kiểm tra dependencies
        if not self._check_dependencies():
            return False
        
        # Tạo thư mục output
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"\n[FOLDER] {self.output_folder}")
        print(f"[URL] {self.playlist_url}")
        print("-" * 60)
        
        # Lấy danh sách video
        print("\n[INFO] Getting playlist info...")
        try:
            videos = self._get_playlist_videos()
        except Exception as e:
            print(f"[ERROR] Failed to get playlist: {e}")
            return False
        
        if not videos:
            print("[ERROR] No videos found in playlist")
            return False
        
        self.total_videos = len(videos)
        print(f"[FOUND] {self.total_videos} videos")
        print("-" * 60)
        print(f"\n[START] Downloading with {self.max_workers} threads...\n")
        
        # Tải song song
        success = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._download_single, video, idx): idx 
                for idx, video in enumerate(videos, 1)
            }
            
            for future in as_completed(futures):
                try:
                    ok, _ = future.result()
                    if ok:
                        success += 1
                    else:
                        failed += 1
                except Exception:
                    failed += 1
        
        # Kết quả
        print("\n" + "=" * 60)
        print(f"[DONE] Completed!")
        print(f"       Success: {success}/{self.total_videos}")
        if failed > 0:
            print(f"       Failed: {failed}")
        print(f"[FOLDER] {self.output_folder}")
        print("=" * 60)
        
        return True


def main():
    """Entry point"""
    downloader = PlaylistDownloader(
        playlist_url=PLAYLIST_URL,
        output_folder=OUTPUT_FOLDER,
        quality=MP3_QUALITY,
        max_workers=MAX_WORKERS
    )
    
    downloader.download()
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()

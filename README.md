# 🎵 YouTube Playlist MP3 Downloader & Music Player

Bộ công cụ tải nhạc MP3 từ playlist YouTube và nghe nhạc offline với giao diện đẹp.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## ✨ Tính năng

### 🎵 Downloader
- 🚀 **Tải đa luồng** - Tải 30+ bài song song
- 🎧 **Chất lượng cao** - Bitrate 320kbps
- 📁 **Tự động tổ chức** - Đánh số thứ tự theo playlist
- ⏸️ **Bỏ qua file đã tải** - Không tải lại
- 🔄 **Tự động retry** - Thử lại khi lỗi mạng

### 🎶 Music Player
- 🖥️ **Giao diện Dark Theme** - Đẹp mắt, hiện đại
- 📃 **Phát lần lượt** - Theo thứ tự
- 🔀 **Ngẫu nhiên** - Random
- 🔀 **Ngẫu nhiên không lặp** - Phát hết list mới lặp
- 💾 **Lưu cache** - Tiếp tục từ lần nghe trước
- ⏩ **Seek** - Kéo thanh thời gian
- 🔊 **Điều chỉnh âm lượng**

## 📋 Yêu cầu

- Python 3.7+
- FFmpeg (đã bao gồm hoặc tự cài)

## 🚀 Cài đặt

```bash
git clone https://github.com/YOUR_USERNAME/youtube-playlist-mp3-downloader.git
cd youtube-playlist-mp3-downloader
pip install -r requirements.txt
```

### FFmpeg

**Windows:** Tải [FFmpeg](https://ffmpeg.org/download.html), đặt `ffmpeg.exe` vào thư mục project.

## 📖 Sử dụng

### 1. Tải playlist

Chỉnh URL trong `auto_download.py`:
```python
PLAYLIST_URL = "https://youtube.com/playlist?list=YOUR_PLAYLIST_ID"
MAX_WORKERS = 30  # Số luồng
```

```bash
python auto_download.py
```

### 2. Lọc file trùng

```bash
python remove_duplicates.py
```

### 3. Nghe nhạc

```bash
python music_player.py
```

## ⚙️ Cấu hình

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `PLAYLIST_URL` | URL playlist YouTube | - |
| `MAX_WORKERS` | Số luồng tải song song | `30` |
| `MP3_QUALITY` | Bitrate (128/192/256/320) | `192` |

## 📁 Cấu trúc

```
├── auto_download.py       # Tải đa luồng
├── download_playlist.py   # Tải tương tác
├── remove_duplicates.py   # Lọc trùng
├── music_player.py        # App nghe nhạc
├── requirements.txt
├── README.md
├── ffmpeg.exe
└── downloads/             # Thư mục MP3
```

## 🔧 Xử lý sự cố

| Lỗi | Giải pháp |
|-----|-----------|
| FFmpeg not found | Đặt `ffmpeg.exe` vào thư mục project |
| Tải chậm | Tăng `MAX_WORKERS`, giảm `MP3_QUALITY` |
| Video unavailable | Tự động bỏ qua |

## 📝 License

MIT License

---
⭐ Nếu hữu ích, hãy star repo!

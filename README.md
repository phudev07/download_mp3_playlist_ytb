# 🎵 YouTube Playlist MP3 Downloader

Công cụ tải nhạc MP3 từ playlist YouTube với tốc độ cao, hỗ trợ đa luồng.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Tính năng

- 🚀 **Tải đa luồng** - Tải nhiều bài song song (mặc định 5 luồng, có thể tăng lên 30+)
- 🎧 **Chất lượng cao** - Hỗ trợ bitrate lên đến 320kbps
- 📁 **Tự động tổ chức** - Đánh số thứ tự và đặt tên file theo tiêu đề
- ⏸️ **Tiếp tục tải** - Bỏ qua file đã tải, không tải lại
- 🔄 **Tự động retry** - Thử lại khi gặp lỗi mạng
- 🌐 **Bypass geo-restriction** - Vượt qua giới hạn vùng

## 📋 Yêu cầu

- Python 3.7+
- FFmpeg (đã bao gồm trong repo hoặc tự tải)

## 🚀 Cài đặt

### 1. Clone repo

```bash
git clone https://github.com/YOUR_USERNAME/youtube-playlist-mp3-downloader.git
cd youtube-playlist-mp3-downloader
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cài đặt FFmpeg

**Cách 1:** Tải [FFmpeg](https://ffmpeg.org/download.html) và đặt `ffmpeg.exe` vào thư mục project

**Cách 2:** Cài đặt qua Chocolatey (Windows):
```bash
choco install ffmpeg
```

**Cách 3:** Cài đặt qua Scoop (Windows):
```bash
scoop install ffmpeg
```

## 📖 Sử dụng

### Chế độ tự động (khuyên dùng)

Chỉnh sửa URL playlist trong file `auto_download.py`:

```python
PLAYLIST_URL = "https://youtube.com/playlist?list=YOUR_PLAYLIST_ID"
MAX_WORKERS = 10  # Số luồng tải song song
MP3_QUALITY = "192"  # Chất lượng: 128, 192, 256, 320
```

Chạy:
```bash
python auto_download.py
```

### Chế độ tương tác

```bash
python download_playlist.py
```

Nhập URL playlist khi được hỏi.

### Lọc file trùng lặp

Sau khi tải xong, nếu có file trùng:

```bash
python remove_duplicates.py
```

Script sẽ tự động phát hiện và xóa các bài hát trùng lặp (giữ lại bản có số thứ tự nhỏ hơn).

## ⚙️ Cấu hình

| Biến | Mô tả | Mặc định |
|------|-------|----------|
| `PLAYLIST_URL` | URL playlist YouTube | - |
| `OUTPUT_FOLDER` | Thư mục lưu file | `./downloads` |
| `MAX_WORKERS` | Số luồng tải song song | `5` |
| `MP3_QUALITY` | Bitrate MP3 (kbps) | `192` |

### Khuyến nghị MAX_WORKERS

| Tốc độ mạng | MAX_WORKERS |
|-------------|-------------|
| Chậm (< 10 Mbps) | 3-5 |
| Trung bình (10-50 Mbps) | 5-10 |
| Nhanh (> 50 Mbps) | 10-30 |

## 📁 Cấu trúc thư mục

```
youtube-playlist-mp3-downloader/
├── auto_download.py      # Script tải tự động (đa luồng)
├── download_playlist.py  # Script tải tương tác
├── requirements.txt      # Dependencies
├── ffmpeg.exe           # FFmpeg binary (Windows)
├── ffprobe.exe          # FFprobe binary (Windows)
├── README.md            # Tài liệu
├── .gitignore           # Git ignore
└── downloads/           # Thư mục chứa file MP3
```

## 🔧 Xử lý sự cố

### Lỗi "FFmpeg not found"
- Đảm bảo `ffmpeg.exe` nằm trong thư mục project
- Hoặc cài FFmpeg vào PATH hệ thống

### Tải chậm
- Tăng `MAX_WORKERS` (tối đa 30)
- Kiểm tra kết nối mạng
- Thử giảm `MP3_QUALITY` xuống 128

### Lỗi "Video unavailable"
- Video có thể bị xóa hoặc private
- Script sẽ tự động bỏ qua và tiếp tục

## 📝 License

MIT License - Tự do sử dụng và chỉnh sửa.

## 🙏 Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Thư viện tải video/audio
- [FFmpeg](https://ffmpeg.org/) - Công cụ xử lý media

---

⭐ Nếu thấy hữu ích, hãy cho repo một star nhé!

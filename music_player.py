#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MP3 Music Player - Desktop App
Ứng dụng nghe nhạc MP3 với giao diện đẹp

Features:
- Phát nhạc MP3 từ thư mục
- Phát ngẫu nhiên (shuffle)
- Phát ngẫu nhiên không lặp (shuffle no repeat)
- Phát lần lượt (sequential)
- Lưu vị trí phát để tiếp tục lần sau
- Giao diện hiện đại

Author: Your Name
License: MIT
"""

import os
import sys
import json
import random
from pathlib import Path

# Kiểm tra và cài đặt dependencies
def install_dependencies():
    required = ['pygame', 'PyQt6', 'mutagen']
    import subprocess
    for pkg in required:
        try:
            __import__(pkg.lower().replace('6', ''))
        except ImportError:
            print(f"Installing {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

install_dependencies()

# Import mutagen để lấy duration MP3
try:
    from mutagen.mp3 import MP3
except ImportError:
    MP3 = None

import pygame
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QListWidget, QListWidgetItem,
    QFileDialog, QStyle, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor


class MusicPlayer(QMainWindow):
    """Main Music Player Window"""
    
    def __init__(self):
        super().__init__()
        
        # Khởi tạo pygame mixer
        pygame.mixer.init()
        
        # Biến state
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.play_mode = "sequential"  # sequential, shuffle, shuffle_no_repeat
        self.shuffle_history = []
        self.shuffle_remaining = []
        
        # Duration tracking
        self.track_duration = 0  # seconds
        self.track_start_time = 0  # thời điểm bắt đầu phát
        
        # Đường dẫn cache
        self.script_dir = Path(__file__).parent.absolute()
        self.cache_file = self.script_dir / "player_cache.json"
        self.music_folder = self.script_dir / "downloads"
        
        # Setup UI
        self.setup_ui()
        self.apply_dark_theme()
        
        # Load cache và playlist
        self.load_cache()
        self.load_music_folder()
        
        # Timer cập nhật progress (500ms cho mượt hơn)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(500)
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        self.setWindowTitle("🎵 MP3 Music Player")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== Header =====
        header = QLabel("🎵 MP3 Music Player")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # ===== Folder Info =====
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel(f"📁 {self.music_folder}")
        self.folder_label.setFont(QFont("Segoe UI", 10))
        folder_layout.addWidget(self.folder_label)
        
        btn_browse = QPushButton("📂 Đổi thư mục")
        btn_browse.clicked.connect(self.browse_folder)
        btn_browse.setFixedWidth(120)
        folder_layout.addWidget(btn_browse)
        layout.addLayout(folder_layout)
        
        # ===== Playlist =====
        self.playlist_widget = QListWidget()
        self.playlist_widget.setFont(QFont("Segoe UI", 11))
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected)
        layout.addWidget(self.playlist_widget, 1)
        
        # ===== Now Playing =====
        now_playing_frame = QFrame()
        now_playing_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        now_playing_layout = QVBoxLayout(now_playing_frame)
        
        self.now_playing_label = QLabel("🎵 Chưa phát nhạc")
        self.now_playing_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.now_playing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.now_playing_label.setWordWrap(True)
        now_playing_layout.addWidget(self.now_playing_label)
        
        # Progress bar
        progress_layout = QHBoxLayout()
        self.time_current = QLabel("0:00")
        self.time_current.setFont(QFont("Segoe UI", 10))
        progress_layout.addWidget(self.time_current)
        
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderReleased.connect(self.seek_position)
        progress_layout.addWidget(self.progress_slider, 1)
        
        self.time_total = QLabel("0:00")
        self.time_total.setFont(QFont("Segoe UI", 10))
        progress_layout.addWidget(self.time_total)
        now_playing_layout.addLayout(progress_layout)
        
        layout.addWidget(now_playing_frame)
        
        # ===== Controls =====
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        # Nút điều khiển
        btn_size = QSize(50, 50)
        
        self.btn_prev = QPushButton("⏮")
        self.btn_prev.setFixedSize(btn_size)
        self.btn_prev.clicked.connect(self.play_previous)
        controls_layout.addWidget(self.btn_prev)
        
        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedSize(QSize(70, 70))
        self.btn_play.setFont(QFont("Segoe UI", 20))
        self.btn_play.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.btn_play)
        
        self.btn_next = QPushButton("⏭")
        self.btn_next.setFixedSize(btn_size)
        self.btn_next.clicked.connect(self.play_next)
        controls_layout.addWidget(self.btn_next)
        
        controls_layout.addSpacing(30)
        
        # Volume
        vol_label = QLabel("🔊")
        vol_label.setFont(QFont("Segoe UI", 14))
        controls_layout.addWidget(vol_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(120)
        self.volume_slider.valueChanged.connect(self.change_volume)
        controls_layout.addWidget(self.volume_slider)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # ===== Play Mode Buttons =====
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)
        
        self.btn_sequential = QPushButton("📃 Lần lượt")
        self.btn_sequential.setCheckable(True)
        self.btn_sequential.setChecked(True)
        self.btn_sequential.clicked.connect(lambda: self.set_play_mode("sequential"))
        mode_layout.addWidget(self.btn_sequential)
        
        self.btn_shuffle = QPushButton("🔀 Ngẫu nhiên")
        self.btn_shuffle.setCheckable(True)
        self.btn_shuffle.clicked.connect(lambda: self.set_play_mode("shuffle"))
        mode_layout.addWidget(self.btn_shuffle)
        
        self.btn_shuffle_no_repeat = QPushButton("🔀 Ngẫu nhiên (không lặp)")
        self.btn_shuffle_no_repeat.setCheckable(True)
        self.btn_shuffle_no_repeat.clicked.connect(lambda: self.set_play_mode("shuffle_no_repeat"))
        mode_layout.addWidget(self.btn_shuffle_no_repeat)
        
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # Set initial volume
        pygame.mixer.music.set_volume(0.7)
    
    def apply_dark_theme(self):
        """Áp dụng dark theme"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1a1a2e;
                color: #eaeaea;
            }
            QPushButton {
                background-color: #16213e;
                color: #eaeaea;
                border: 2px solid #0f3460;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0f3460;
                border-color: #e94560;
            }
            QPushButton:checked {
                background-color: #e94560;
                border-color: #e94560;
            }
            QListWidget {
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #e94560;
            }
            QListWidget::item:hover {
                background-color: #0f3460;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: #16213e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                width: 18px;
                height: 18px;
                margin: -5px 0;
                background: #e94560;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #e94560;
                border-radius: 4px;
            }
            QFrame {
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: #eaeaea;
            }
        """)
    
    def load_music_folder(self):
        """Load nhạc từ thư mục"""
        self.playlist = []
        self.playlist_widget.clear()
        
        if not self.music_folder.exists():
            self.music_folder.mkdir(parents=True, exist_ok=True)
        
        mp3_files = sorted(self.music_folder.glob("*.mp3"))
        
        for f in mp3_files:
            self.playlist.append(str(f))
            # Hiển thị tên đẹp hơn
            display_name = f.stem
            item = QListWidgetItem(f"🎵 {display_name}")
            self.playlist_widget.addItem(item)
        
        self.folder_label.setText(f"📁 {self.music_folder} ({len(self.playlist)} bài)")
        
        # Reset shuffle remaining
        self.shuffle_remaining = list(range(len(self.playlist)))
        random.shuffle(self.shuffle_remaining)
    
    def browse_folder(self):
        """Chọn thư mục nhạc"""
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục nhạc", str(self.music_folder))
        if folder:
            self.music_folder = Path(folder)
            self.load_music_folder()
            self.save_cache()
    
    def play_selected(self, item):
        """Phát bài được chọn"""
        idx = self.playlist_widget.row(item)
        self.play_track(idx)
    
    def get_track_duration(self, filepath: str) -> int:
        """Lấy duration của file MP3 (seconds)"""
        try:
            if MP3:
                audio = MP3(filepath)
                return int(audio.info.length)
        except Exception:
            pass
        return 0
    
    def play_track(self, index: int):
        """Phát một bài hát"""
        if not self.playlist or index < 0 or index >= len(self.playlist):
            return
        
        self.current_index = index
        track_path = self.playlist[index]
        
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.btn_play.setText("⏸")
            
            # Lấy duration
            self.track_duration = self.get_track_duration(track_path)
            self.track_start_time = 0
            
            # Cập nhật UI duration
            if self.track_duration > 0:
                mins, secs = divmod(self.track_duration, 60)
                self.time_total.setText(f"{mins}:{secs:02d}")
                self.progress_slider.setRange(0, self.track_duration)
                self.progress_slider.setValue(0)
            else:
                self.time_total.setText("--:--")
            
            self.time_current.setText("0:00")
            
            # Update UI
            track_name = Path(track_path).stem
            self.now_playing_label.setText(f"🎵 {track_name}")
            self.playlist_widget.setCurrentRow(index)
            
            # Update shuffle history
            if self.play_mode == "shuffle_no_repeat":
                if index in self.shuffle_remaining:
                    self.shuffle_remaining.remove(index)
                self.shuffle_history.append(index)
            
            self.save_cache()
            
        except Exception as e:
            print(f"Error playing: {e}")
    
    def toggle_play(self):
        """Play/Pause"""
        if not self.playlist:
            return
        
        if not self.is_playing:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                self.play_track(self.current_index)
            self.is_playing = True
            self.btn_play.setText("⏸")
        else:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            self.btn_play.setText("▶")
    
    def play_next(self):
        """Phát bài tiếp theo"""
        if not self.playlist:
            return
        
        if self.play_mode == "sequential":
            next_idx = (self.current_index + 1) % len(self.playlist)
        
        elif self.play_mode == "shuffle":
            next_idx = random.randint(0, len(self.playlist) - 1)
        
        elif self.play_mode == "shuffle_no_repeat":
            if not self.shuffle_remaining:
                # Reset khi hết vòng
                self.shuffle_remaining = list(range(len(self.playlist)))
                random.shuffle(self.shuffle_remaining)
                self.shuffle_history = []
            next_idx = self.shuffle_remaining[0]
        
        else:
            next_idx = (self.current_index + 1) % len(self.playlist)
        
        self.play_track(next_idx)
    
    def play_previous(self):
        """Phát bài trước"""
        if not self.playlist:
            return
        
        if self.play_mode == "shuffle_no_repeat" and self.shuffle_history:
            # Quay lại bài trước trong history
            if len(self.shuffle_history) > 1:
                self.shuffle_history.pop()  # Bỏ bài hiện tại
                prev_idx = self.shuffle_history[-1]
            else:
                prev_idx = self.shuffle_history[0]
        else:
            prev_idx = (self.current_index - 1) % len(self.playlist)
        
        self.play_track(prev_idx)
    
    def set_play_mode(self, mode: str):
        """Đổi chế độ phát"""
        self.play_mode = mode
        
        # Update button states
        self.btn_sequential.setChecked(mode == "sequential")
        self.btn_shuffle.setChecked(mode == "shuffle")
        self.btn_shuffle_no_repeat.setChecked(mode == "shuffle_no_repeat")
        
        # Reset shuffle state khi đổi mode
        if mode == "shuffle_no_repeat":
            self.shuffle_remaining = list(range(len(self.playlist)))
            random.shuffle(self.shuffle_remaining)
            self.shuffle_history = [self.current_index] if self.playlist else []
        
        self.save_cache()
    
    def change_volume(self, value: int):
        """Thay đổi âm lượng"""
        pygame.mixer.music.set_volume(value / 100)
    
    def seek_position(self):
        """Seek đến vị trí khi user kéo slider"""
        if (self.is_playing or self.is_paused) and self.track_duration > 0:
            seek_pos = self.progress_slider.value()
            try:
                # Pygame seek bằng cách play lại từ vị trí mới
                pygame.mixer.music.play(start=seek_pos)
                self.track_start_time = seek_pos
                if self.is_paused:
                    pygame.mixer.music.pause()
            except Exception as e:
                print(f"Seek error: {e}")
    
    def update_progress(self):
        """Cập nhật progress bar mỗi giây"""
        if self.is_playing and pygame.mixer.music.get_busy():
            # Tính thời gian hiện tại
            pos_ms = pygame.mixer.music.get_pos()  # milliseconds từ lúc play
            if pos_ms >= 0:
                current_pos = self.track_start_time + (pos_ms // 1000)
                
                # Cập nhật time label
                mins, secs = divmod(current_pos, 60)
                self.time_current.setText(f"{mins}:{secs:02d}")
                
                # Cập nhật slider (không trigger signal)
                if not self.progress_slider.isSliderDown():
                    self.progress_slider.setValue(current_pos)
        
        # Auto play next khi hết bài
        if self.is_playing and not pygame.mixer.music.get_busy() and not self.is_paused:
            self.play_next()
    
    def save_cache(self):
        """Lưu trạng thái"""
        cache = {
            "music_folder": str(self.music_folder),
            "current_index": self.current_index,
            "play_mode": self.play_mode,
            "shuffle_history": self.shuffle_history,
            "shuffle_remaining": self.shuffle_remaining,
            "volume": self.volume_slider.value()
        }
        
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def load_cache(self):
        """Load trạng thái đã lưu"""
        if not self.cache_file.exists():
            return
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            if "music_folder" in cache:
                self.music_folder = Path(cache["music_folder"])
            
            if "current_index" in cache:
                self.current_index = cache["current_index"]
            
            if "play_mode" in cache:
                self.set_play_mode(cache["play_mode"])
            
            if "shuffle_history" in cache:
                self.shuffle_history = cache["shuffle_history"]
            
            if "shuffle_remaining" in cache:
                self.shuffle_remaining = cache["shuffle_remaining"]
            
            if "volume" in cache:
                self.volume_slider.setValue(cache["volume"])
                pygame.mixer.music.set_volume(cache["volume"] / 100)
            
        except Exception as e:
            print(f"Error loading cache: {e}")
    
    def closeEvent(self, event):
        """Lưu cache khi đóng app"""
        self.save_cache()
        pygame.mixer.quit()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    
    player = MusicPlayer()
    player.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

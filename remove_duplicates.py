#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lọc nhạc trùng lặp trong thư mục downloads
Dựa trên tên file và kích thước file
"""

import os
import sys
import hashlib
from pathlib import Path
from collections import defaultdict
import re

# Fix encoding cho Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def normalize_title(filename: str) -> str:
    """Chuẩn hóa tên file để so sánh"""
    # Bỏ số thứ tự đầu file (001 - , 002 - , ...)
    name = re.sub(r'^\d{1,4}\s*[-_\.]\s*', '', filename)
    # Bỏ extension
    name = Path(name).stem
    # Chuyển lowercase
    name = name.lower()
    # Bỏ ký tự đặc biệt, giữ chữ và số
    name = re.sub(r'[^\w\s]', '', name)
    # Bỏ khoảng trắng thừa
    name = ' '.join(name.split())
    return name


def get_file_hash(filepath: Path, chunk_size: int = 8192) -> str:
    """Tính MD5 hash của file"""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        # Chỉ hash 1MB đầu để nhanh hơn
        data = f.read(1024 * 1024)
        hasher.update(data)
    return hasher.hexdigest()


def find_duplicates(folder: Path) -> dict:
    """Tìm file trùng lặp dựa trên tên chuẩn hóa"""
    mp3_files = list(folder.glob("*.mp3"))
    
    # Group theo tên chuẩn hóa
    groups = defaultdict(list)
    for f in mp3_files:
        normalized = normalize_title(f.name)
        groups[normalized].append(f)
    
    # Lọc chỉ lấy những nhóm có > 1 file
    duplicates = {k: v for k, v in groups.items() if len(v) > 1}
    return duplicates


def remove_duplicates(folder: Path, dry_run: bool = True) -> int:
    """
    Xóa file trùng lặp, giữ lại file có số thứ tự nhỏ nhất
    
    Args:
        folder: Thư mục chứa file
        dry_run: True = chỉ hiển thị, False = xóa thật
    
    Returns:
        Số file đã xóa
    """
    duplicates = find_duplicates(folder)
    
    if not duplicates:
        print("[OK] Khong tim thay file trung lap!")
        return 0
    
    removed = 0
    
    print(f"\n[FOUND] Tim thay {len(duplicates)} nhom file trung lap:\n")
    
    for title, files in duplicates.items():
        # Sắp xếp theo số thứ tự (file có số nhỏ giữ lại)
        files_sorted = sorted(files, key=lambda x: x.name)
        keep = files_sorted[0]
        to_remove = files_sorted[1:]
        
        print(f"  [{title[:50]}...]")
        print(f"    GIU: {keep.name}")
        
        for f in to_remove:
            print(f"    XOA: {f.name}")
            if not dry_run:
                try:
                    f.unlink()
                    removed += 1
                except Exception as e:
                    print(f"    [ERROR] Khong xoa duoc: {e}")
        print()
    
    return removed


def main():
    """Entry point"""
    print("=" * 60)
    print("   LOC NHAC TRUNG LAP")
    print("=" * 60)
    
    script_dir = Path(__file__).parent.absolute()
    downloads_folder = script_dir / "downloads"
    
    if not downloads_folder.exists():
        print(f"[ERROR] Khong tim thay thu muc: {downloads_folder}")
        input("\nNhan Enter de thoat...")
        return
    
    # Đếm file MP3
    mp3_count = len(list(downloads_folder.glob("*.mp3")))
    print(f"\n[INFO] Thu muc: {downloads_folder}")
    print(f"[INFO] Tong so file MP3: {mp3_count}")
    print("-" * 60)
    
    # Tìm duplicates (dry run)
    duplicates = find_duplicates(downloads_folder)
    
    if not duplicates:
        print("\n[OK] Khong co file trung lap!")
        input("\nNhan Enter de thoat...")
        return
    
    # Hiển thị và hỏi xác nhận
    total_to_remove = sum(len(v) - 1 for v in duplicates.values())
    
    print(f"\n[FOUND] {len(duplicates)} nhom trung lap ({total_to_remove} file se bi xoa)")
    print("-" * 60)
    
    # Hiển thị preview
    remove_duplicates(downloads_folder, dry_run=True)
    
    # Xác nhận xóa
    print("-" * 60)
    confirm = input("\nBan co muon XOA cac file trung lap? (y/n): ").strip().lower()
    
    if confirm == 'y':
        removed = remove_duplicates(downloads_folder, dry_run=False)
        print(f"\n[DONE] Da xoa {removed} file trung lap!")
        
        # Đếm lại
        new_count = len(list(downloads_folder.glob("*.mp3")))
        print(f"[INFO] Con lai: {new_count} file MP3")
    else:
        print("\n[CANCELLED] Khong xoa gi ca.")
    
    input("\nNhan Enter de thoat...")


if __name__ == "__main__":
    main()

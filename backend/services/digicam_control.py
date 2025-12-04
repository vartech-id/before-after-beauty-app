# backend/services/digicam_control.py
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

from backend.config import (
    DIGICAM_BASE_URL,
    DIGICAM_PREVIEW_PATH,
    DIGICAM_CAPTURE_CMD,
)


def _build_url(path_or_query: str) -> str:
    """
    Gabungkan base URL digiCamControl dengan path atau query.
    Kalau sudah diawali http/https, kembalikan apa adanya.
    """
    if path_or_query.startswith("http://") or path_or_query.startswith("https://"):
        return path_or_query
    return DIGICAM_BASE_URL.rstrip("/") + path_or_query


def trigger_capture() -> None:
    """
    Minta digiCamControl untuk jepret foto.
    Menggunakan webserver command: /?CMD=Capture
    """
    url = _build_url(DIGICAM_CAPTURE_CMD)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()


def get_preview_image() -> tuple[bytes, str]:
    """
    Ambil gambar dari digiCamControl (liveview/preview).
    Return: (bytes_image, content_type)
    """
    url = _build_url(DIGICAM_PREVIEW_PATH)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "image/jpeg")
    return resp.content, content_type


def _get_latest_file(directory: Path) -> Optional[Path]:
    """
    Ambil file terbaru (berdasarkan mtime) dari sebuah folder.
    Hanya mempertimbangkan file biasa, bukan folder.
    """
    if not directory.exists():
        return None

    files = [p for p in directory.iterdir() if p.is_file()]
    if not files:
        return None

    return max(files, key=lambda p: p.stat().st_mtime)


def capture_and_save_photo(original_dir: Path, output_dir: Path) -> str:
    """
    1. Trigger capture di digiCamControl (kamera jepret)
    2. Tunggu file baru muncul di folder original_dir (folder digiCamControl)
    3. Copy file baru itu ke output_dir (backend/static/photos)
    4. Return nama file (bukan path lengkap)

    original_dir: folder tempat digiCamControl menyimpan foto asli
    output_dir: folder tujuan untuk file final yang diakses web
    """
    if not original_dir.exists():
        raise RuntimeError(f"Original directory does not exist: {original_dir}")

    # Catat file terbaru sebelum capture
    before_file = _get_latest_file(original_dir)
    before_mtime = before_file.stat().st_mtime if before_file else None

    # 1. Jepret
    trigger_capture()

    # 2. Tunggu file baru muncul
    latest_file: Optional[Path] = None
    timeout_seconds = 5.0
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        time.sleep(0.5)
        candidate = _get_latest_file(original_dir)
        if not candidate:
            continue

        if before_mtime is None:
            # Tidak ada file sebelumnya, file apa pun dianggap baru
            latest_file = candidate
            break

        # Jika ada file baru dengan mtime lebih besar dari sebelumnya, pakai itu
        if candidate.stat().st_mtime > before_mtime:
            latest_file = candidate
            break

    if latest_file is None:
        raise RuntimeError("No new file detected in digiCamControl folder after capture")

    # 3. Pastikan folder output ada
    output_dir.mkdir(parents=True, exist_ok=True)

    # Bisa pakai nama asli kamera, atau diberi prefix timestamp agar unik
    timestamp_prefix = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    dest_name = f"{timestamp_prefix}_{latest_file.name}"
    dest_path = output_dir / dest_name

    shutil.copy2(latest_file, dest_path)

    return dest_name

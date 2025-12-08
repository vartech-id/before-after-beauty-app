# backend/config.py
import os
from pathlib import Path

# Base directory (folder "backend")
BASE_DIR = Path(__file__).resolve().parent

# Static directory: backend/static
STATIC_DIR = BASE_DIR / "static"

# Folder untuk menyimpan hasil foto original dari kamera: backend/static/captured
CAPTURED_DIR = STATIC_DIR / "captured"

# Folder untuk menyimpan hasil filter (after) tanpa kompresi: backend/static/after
AFTER_DIR = STATIC_DIR / "after"

# Folder untuk menyimpan final result (jika ada post-processing lanjutan)
RESULT_DIR = STATIC_DIR / "result"

# Folder asli tempat digiCamControl menyimpan foto dari kamera
# Default diset ke path yang kamu berikan, tapi bisa dioverride pakai env DIGICAM_ORIGINAL_DIR
DIGICAM_ORIGINAL_DIR = Path(
    os.getenv(
        "DIGICAM_ORIGINAL_DIR",
        r"C:\Users\flip3\Pictures\digiCamControl\test samuel",
    )
)

# URL backend ini sendiri (dipakai untuk membangun photo_url absolute)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Konfigurasi digiCamControl webserver
# Default: http://127.0.0.1:5513
DIGICAM_BASE_URL = os.getenv("DIGICAM_BASE_URL", "http://127.0.0.1:5513")

# Path untuk live view di digiCamControl webserver
# Kita pakai /liveview.jpg untuk preview/live view
DIGICAM_PREVIEW_PATH = os.getenv("DIGICAM_PREVIEW_PATH", "/liveview.jpg")
DIGICAM_CAPTURE_CMD = os.getenv("DIGICAM_CAPTURE_CMD", "/?CMD=Capture")

PREDICTOR_PATH = BASE_DIR / "shape_predictor_68_face_landmarks.dat"

# CORS: asal frontend yang diizinkan akses API
FRONTEND_ORIGINS = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

# GDRIVE
# Allow insecure transport for local development (http://localhost)
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

# OAuth token persistence (use absolute paths so uvicorn cwd tidak bermasalah)
TOKEN_FILE = os.getenv("TOKEN_FILE", str(BASE_DIR / "token.json"))
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE", str(BASE_DIR / "client_secrets.json"))

# OAuth scopes
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Google Drive & local watcher defaults
TARGET_FOLDER_ID = os.getenv("TARGET_FOLDER_ID", "1PKm4EjaKmV6DM57i3Wzg7u2Cwc1zlQDY")
# default ke folder RESULT_DIR (absolute path) supaya watcher bekerja pasti
LOCAL_FOLDER_PATH = os.getenv("LOCAL_FOLDER_PATH", str(RESULT_DIR))

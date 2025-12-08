import os
import time
from typing import Dict, Optional

from googleapiclient.http import MediaFileUpload

from backend.config import TARGET_FOLDER_ID
from backend.models.processed_file import ProcessedFile
from backend.services.auth_service import get_drive_service

PROCESSED_FILES: Dict[str, ProcessedFile] = {}
FILES_IN_PROGRESS: set[str] = set()
LATEST_PROCESSED_FILE_ID: str | None = None


def mark_in_progress(file_path: str):
    FILES_IN_PROGRESS.add(file_path)


def discard_in_progress(file_path: str):
    FILES_IN_PROGRESS.discard(file_path)


def is_in_progress(file_path: str) -> bool:
    return file_path in FILES_IN_PROGRESS


def get_processed_files_history() -> Dict[str, ProcessedFile]:
    return PROCESSED_FILES


def get_processed_file(file_id: str) -> Optional[ProcessedFile]:
    return PROCESSED_FILES.get(file_id)


def get_latest_processed_file() -> Optional[ProcessedFile]:
    if LATEST_PROCESSED_FILE_ID:
        return PROCESSED_FILES.get(LATEST_PROCESSED_FILE_ID)
    return None


async def upload_file_to_drive(file_path: str):
    """Upload a local file to Google Drive and track it in memory."""
    global LATEST_PROCESSED_FILE_ID

    service = get_drive_service()
    upload_success = False

    if not service:
        print(f"ERROR: Drive Service tidak tersedia saat mengunggah {file_path}")
        discard_in_progress(file_path)
        return

    file_name = os.path.basename(file_path)
    absolute_path = os.path.abspath(file_path)
    print(f"-> Mengunggah file: {file_name} dari {absolute_path}")

    try:
        file_metadata = {"name": file_name, "parents": [TARGET_FOLDER_ID]}
        media = MediaFileUpload(absolute_path, resumable=True)

        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id, webViewLink, webContentLink")
            .execute()
        )

        processed = ProcessedFile(
            id=file["id"],
            name=file_name,
            share_link=file.get("webViewLink"),
            download_link=file.get("webContentLink"),
            processed_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        )

        PROCESSED_FILES[processed.id] = processed
        LATEST_PROCESSED_FILE_ID = processed.id

        print(f"   [SUCCESS] File {file_name} berhasil diunggah. Drive ID: {processed.id}")
        upload_success = True

    except Exception as e:
        if "No such file or directory" in str(e):
            print(f"   [WARNING] File {file_name} tidak ditemukan (mungkin dihapus/dipindahkan). Melewati.")
        else:
            print(f"   [ERROR] Gagal mengunggah file {file_name}: {e}")
    finally:
        discard_in_progress(file_path)

        if upload_success:
            print(f"   [INFO] File lokal {file_name} dibiarkan tersimpan setelah unggah.")

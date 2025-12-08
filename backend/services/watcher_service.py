import asyncio
import os
import time
from typing import Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config import LOCAL_FOLDER_PATH
from services.drive_service import is_in_progress, mark_in_progress, upload_file_to_drive

observer: Optional[Observer] = None
MAIN_ASYNC_LOOP = None


class LocalChangeHandler(FileSystemEventHandler):
    """Forward filesystem events to the main asyncio loop."""

    def on_created(self, event):
        global MAIN_ASYNC_LOOP

        if event.is_directory or is_in_progress(event.src_path):
            return

        file_path = event.src_path

        # Debounce to ensure the file is fully written before upload
        time.sleep(1)

        if os.path.exists(file_path) and not os.path.basename(file_path).startswith("."):
            print(f"[WATCH] File baru terdeteksi: {file_path}")
            mark_in_progress(file_path)

            if MAIN_ASYNC_LOOP:
                asyncio.run_coroutine_threadsafe(upload_file_to_drive(file_path), MAIN_ASYNC_LOOP)
            else:
                print("ERROR: MAIN_ASYNC_LOOP belum disiapkan. Sinkronisasi gagal.")


def set_main_async_loop(loop):
    global MAIN_ASYNC_LOOP
    MAIN_ASYNC_LOOP = loop


def start_local_watcher():
    """Start monitoring the configured local folder."""
    global observer

    if not os.path.exists(LOCAL_FOLDER_PATH):
        os.makedirs(LOCAL_FOLDER_PATH)
        print(f"[SETUP] Folder lokal dibuat: {LOCAL_FOLDER_PATH}")

    event_handler = LocalChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, LOCAL_FOLDER_PATH, recursive=False)
    observer.start()
    print(f"[WATCHER] Mulai memantau folder lokal: {LOCAL_FOLDER_PATH}")


def stop_local_watcher():
    """Stop monitoring the local folder."""
    global observer

    if observer:
        observer.stop()
        observer.join()
        print("[WATCHER] Pemantauan folder lokal dihentikan.")

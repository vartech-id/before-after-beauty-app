import base64
import json
import io
from pathlib import Path

import requests
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from PIL import Image

from backend.config import AFTER_DIR, RESULT_DIR, API_BASE_URL, STATIC_DIR
from backend.models.presets import VALID_PRESETS, as_dict_map, merge_config, update_preset
from backend.services.beautify import beautify_image
from backend.services.storage import save_image_lossless, save_image_jpeg

import qrcode
from fastapi import Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse

from backend.config import LOCAL_FOLDER_PATH, TARGET_FOLDER_ID
from backend.schemas.drive import DriveFile, TestDriveResponse
from backend.services import auth_service, drive_service

router = APIRouter(prefix="/api")


class PresetUpdateRequest(BaseModel):
    target_L: float | None = None
    max_delta_L: float | None = None
    smooth_strength: float | None = None
    eye_smooth_strength: float | None = None
    glow_strength: float | None = None
    saturation_boost: float | None = None
    hydration_highlight: float | None = None
    wrinkle_soften: float | None = None
    detail_mix: float | None = None
    unsharp_amount: float | None = None
    unsharp_radius: float | None = None
    edge_enhance_mix: float | None = None


@router.get("/presets")
async def list_presets():
    """Return all current preset values."""
    return {"presets": as_dict_map()}


@router.post("/presets/preview")
async def preset_preview(request: Request):
    """
    Accept multipart form (image, preset, config) and return a JPEG preview.
    Using manual form parsing to avoid UTF-8 decode issues when binary is malformed.
    """
    form = await request.form()

    image = form.get("image")
    preset_key = str(form.get("preset") or "").lower()
    config_raw = form.get("config") or ""

    if not image:
        raise HTTPException(status_code=400, detail="Field 'image' wajib diisi (file).")
    if preset_key not in VALID_PRESETS:
        raise HTTPException(status_code=400, detail="Preset tidak dikenal")

    try:
        overrides = json.loads(config_raw) if config_raw else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Config harus JSON yang valid")

    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="File gambar tidak valid")

    merged_cfg = merge_config(preset_key, overrides)
    out_img = beautify_image(img, preset_key, config_override=merged_cfg)

    buffer = io.BytesIO()
    out_img.save(buffer, format="JPEG", quality=95)
    buffer.seek(0)

    return Response(content=buffer.read(), media_type="image/jpeg")


@router.post("/presets/{preset}")
async def save_preset(preset: str, payload: PresetUpdateRequest):
    preset_key = preset.lower()
    if preset_key not in VALID_PRESETS:
        raise HTTPException(status_code=400, detail="Preset tidak dikenal")

    updated_cfg = update_preset(preset_key, payload.dict(exclude_none=True))
    return {"preset": preset_key, "config": as_dict_map()[preset_key]}


@router.post("/beauty")
async def beauty_endpoint(
    image: UploadFile = File(...),
    preset: str = Form(...),
):
    preset = preset.lower()
    if preset not in VALID_PRESETS:
        raise HTTPException(status_code=400, detail="Preset tidak dikenal")

    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="File gambar tidak valid")

    out_img = beautify_image(img, preset)

    # Simpan hasil filter ke folder after saja (lossless PNG, kualitas asli)
    after_filename = save_image_lossless(out_img, AFTER_DIR, prefix="after")
    after_url = f"{API_BASE_URL.rstrip('/')}/static/after/{after_filename}"

    buffer = io.BytesIO()
    out_img.save(buffer, format="JPEG", quality=95)
    buffer.seek(0)

    return Response(
        content=buffer.read(),
        media_type="image/jpeg",
        headers={
          "X-After-Url": after_url,
          "Access-Control-Expose-Headers": "X-After-Url",
        },
    )


# =========================
# Render final result (before + after + overlay)
# =========================

class SlotRel(BaseModel):
    x: float
    y: float
    w: float
    h: float


class RenderResultRequest(BaseModel):
    before_url: str
    after_url: str
    overlay_enabled: bool = True
    overlay_mode: str = "template"  # "template" | "logic"
    overlay_src: str | None = None  # data URL atau URL jika template
    overlay_rel: SlotRel
    photo1_rel: SlotRel
    photo2_rel: SlotRel
    filter_code: str | None = None
    canvas_width: int = 2400
    canvas_height: int = 3600


def _load_image_from_source(src: str) -> Image.Image:
    if src.startswith("data:"):
        try:
            header, b64data = src.split(",", 1)
            binary = base64.b64decode(b64data)
            return Image.open(io.BytesIO(binary)).convert("RGBA")
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail="Invalid data URL") from exc
    if src.startswith("http://") or src.startswith("https://"):
        resp = requests.get(src, timeout=15)
        if not resp.ok:
            raise HTTPException(status_code=400, detail=f"Failed to fetch image: {src}")
        return Image.open(io.BytesIO(resp.content)).convert("RGBA")

    # fallback: treat as local path
    path = Path(src)
    if not path.exists():
        raise HTTPException(status_code=400, detail=f"Image path not found: {src}")
    return Image.open(path).convert("RGBA")


def _place_cover(canvas: Image.Image, img: Image.Image, rel: SlotRel) -> None:
    cw, ch = canvas.size
    x = int(rel.x * cw)
    y = int(rel.y * ch)
    w = max(1, int(rel.w * cw))
    h = max(1, int(rel.h * ch))

    scale = max(w / img.width, h / img.height)
    new_w = int(img.width * scale)
    new_h = int(img.height * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    offset_x = max(0, (new_w - w) // 2)
    offset_y = max(0, (new_h - h) // 2)
    cropped = resized.crop((offset_x, offset_y, offset_x + w, offset_y + h))

    canvas.alpha_composite(cropped, dest=(x, y))


@router.post("/render-result")
def render_result(req: RenderResultRequest):
    try:
        before_img = _load_image_from_source(req.before_url)
        after_img = _load_image_from_source(req.after_url)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Gagal memuat gambar: {exc}") from exc

    canvas = Image.new("RGBA", (req.canvas_width, req.canvas_height), (255, 255, 255, 255))

    _place_cover(canvas, before_img, req.photo1_rel)
    _place_cover(canvas, after_img, req.photo2_rel)

    # overlay logic / template
    if req.overlay_enabled:
        overlay_img = None
        if req.overlay_mode == "template" and req.overlay_src:
            overlay_img = _load_image_from_source(req.overlay_src)
        elif req.overlay_mode == "logic" and req.filter_code:
            overlay_map = {
                "MENCERAHKAN_KULIT": STATIC_DIR / "overlays" / "overlay_mencerahkan.png",
                "MENGURANGI_KERIPUT": STATIC_DIR / "overlays" / "overlay_keriput.png",
                "MELEMBABKAN_KULIT": STATIC_DIR / "overlays" / "overlay_melembabkan.png",
            }
            path = overlay_map.get(req.filter_code)
            if path and path.exists():
                overlay_img = Image.open(path).convert("RGBA")

        if overlay_img:
            cw, ch = canvas.size
            x = int(req.overlay_rel.x * cw)
            y = int(req.overlay_rel.y * ch)
            w = max(1, int(req.overlay_rel.w * cw))
            h = max(1, int(req.overlay_rel.h * ch))
            overlay_resized = overlay_img.resize((w, h), Image.LANCZOS)
            canvas.alpha_composite(overlay_resized, dest=(x, y))

    # Simpan versi share-friendly (JPEG) di folder result
    filename = save_image_jpeg(canvas, RESULT_DIR, prefix="result", quality=92)
    result_url = f"{API_BASE_URL.rstrip('/')}/static/result/{filename}"

    return JSONResponse({"result_url": result_url, "file_name": filename})


@router.get("/drive/latest")
async def latest_drive_file():
    """Get latest uploaded Drive file (from watcher uploads)."""
    latest = drive_service.get_latest_processed_file()
    if not latest:
        raise HTTPException(status_code=404, detail="Belum ada file terunggah.")

    qr_url = f"{API_BASE_URL.rstrip('/')}/api/qr/{latest.id}"
    return {
        "id": latest.id,
        "name": latest.name,
        "share_link": latest.share_link,
        "download_link": latest.download_link,
        "qr_url": qr_url,
        "processed_time": latest.processed_time,
    }

@router.get("/qr/{file_id}", tags=["QR Code"], response_class=StreamingResponse)
async def qr_code_generator(file_id: str):
    """Generate a QR code for a Drive share link."""
    file_data = drive_service.get_processed_file(file_id)
    if not file_data:
        return RedirectResponse(url="/", status_code=status.HTTP_404_NOT_FOUND)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(file_data.share_link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")


@router.get("/", response_class=HTMLResponse, tags=["Sinkronisasi Status"])
async def home():
    """Landing page: shows sync status or prompts authorization."""
    if auth_service.is_authorized():
        latest_file_html = ""
        latest = drive_service.get_latest_processed_file()

        if latest:
            qr_link = f"/qr/{latest.id}"
            preview_link = latest.share_link

            latest_file_html = f"""
            <h3 class="text-xl font-semibold mb-4 text-gray-800">File Terakhir Diunggah:</h3>
            <div class="flex flex-col md:flex-row items-stretch justify-center gap-6 p-6 border border-indigo-200 rounded-xl shadow-lg bg-white">
                <div class="flex-1 flex flex-col items-center justify-center p-4 bg-indigo-50/50 rounded-lg">
                    <p class="text-2xl font-bold mb-3 text-indigo-700 break-words text-center">{latest.name}</p>
                    <p class="text-sm font-medium mb-1 text-gray-600">Diunggah pada: {latest.processed_time}</p>
                    <p class="text-lg font-medium mt-3 mb-2 text-gray-800">Tautan Drive:</p>
                    <a href="{preview_link}" target="_blank" class="text-blue-600 hover:text-blue-800 underline break-words text-center text-sm p-2 bg-white rounded-md border border-gray-200 w-full max-w-xs">
                        {preview_link.split('//')[1].split('/')[0]}...
                    </a>
                </div>
                <div class="flex-none flex flex-col items-center justify-center p-4 bg-white border border-gray-200 rounded-lg shadow-inner">
                    <p class="text-md font-medium mb-3 text-gray-600">Scan untuk Akses:</p>
                    <img src="{qr_link}" alt="QR Code untuk {latest.name}" class="w-48 h-48 border-4 border-gray-100 rounded-lg shadow-xl">
                </div>
            </div>
            """
        else:
            latest_file_html = "<p class='mt-4 text-red-500'>Belum ada file yang diunggah sejak server dimulai.</p>"

        history = drive_service.get_processed_files_history()
        file_list_html = ""
        if history:
            file_list_html = "<ul class='space-y-2'>"
            for file_id, data in history.items():
                file_list_html += f"<li class='flex justify-between items-center text-sm'><span class='font-medium text-gray-700'>**{data.name}**</span><a href='{data.share_link}' target='_blank' class='text-xs text-blue-500 hover:text-blue-700 underline'>Link Drive</a></li>"
            file_list_html += "</ul>"
        else:
            file_list_html = "<p class='text-sm text-gray-500'>Riwayat kosong.</p>"

        return f"""
        <html>
            <head>
                <title>Status Sinkronisasi Lokal -> Drive</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <style>
                    body {{ font-family: 'Inter', sans-serif; }}
                </style>
            </head>
            <body class="bg-gray-50 min-h-screen">
                <div class="max-w-4xl mx-auto p-6 lg:p-12">
                    <h1 class="text-3xl font-bold mb-8 text-gray-900 border-b pb-3">FastAPI Local Drive Sync</h1>
                    
                    <div class="p-6 bg-green-50 border border-green-300 rounded-xl mb-10 shadow-md">
                        <h2 class="text-xl font-semibold text-green-800">Status: Sudah Terotorisasi (Aktif)</h2>
                        <p class="mt-2 text-sm text-green-700">Folder Lokal Diawasi: <code>{LOCAL_FOLDER_PATH}</code></p>
                        <p class="text-sm text-green-700">Folder Drive Target: <code>{TARGET_FOLDER_ID}</code></p>
                        <a href="/test-drive" class="mt-3 inline-block text-blue-600 hover:text-blue-800 text-sm font-medium">[Coba Panggil Drive API (Uji Koneksi)]</a>
                    </div>
                    
                    {latest_file_html}

                    <hr class="my-10 border-gray-300">

                    <h3 class="text-xl font-semibold mb-4 text-gray-800">Riwayat Sinkronisasi (Sejak Server Dimulai):</h3>
                    <div class="bg-white p-4 rounded-lg shadow-md max-h-60 overflow-y-auto border border-gray-100">
                        {file_list_html}
                    </div>
                </div>
            </body>
        </html>
        """

    flow = auth_service.create_flow()
    auth_url, _ = flow.authorization_url(prompt="consent")

    return f"""
    <html>
        <head>
            <title>Perlu Otorisasi</title>
            <style>body{{font-family: sans-serif; padding: 20px;}}</style>
        </head>
        <body>
            <h2>Perhatian: Aplikasi Perlu Izin Google Drive</h2>
            <p>Klik tombol di bawah ini untuk memulai proses otorisasi. Ini hanya perlu dilakukan sekali.</p>
            <a href="{auth_url}">
                <button style="padding: 10px 20px; font-size: 16px; cursor: pointer;">
                    Berikan Izin ke Google Drive
                </button>
            </a>
            <p>Pastikan <code>client_secrets.json</code> dan folder lokal <code>{LOCAL_FOLDER_PATH}</code> sudah siap.</p>
        </body>
    </html>
    """


@router.get("/oauth2callback", tags=["Sinkronisasi Status"])
async def oauth2callback(request: Request):
    """Handle OAuth callback and persist refresh token."""
    auth_service.handle_callback(str(request.url))
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@router.get("/test-drive", response_model=TestDriveResponse, tags=["Test"])
async def test_drive_api():
    """Simple health check against the Drive API."""
    service = auth_service.get_drive_service()
    if not service:
        return TestDriveResponse(
            status="error",
            message="API Service belum terotorisasi atau dimuat.",
        )

    try:
        results = (
            service.files()
            .list(pageSize=10, fields="nextPageToken, files(id, name, mimeType)")
            .execute()
        )

        files = results.get("files", [])
        return TestDriveResponse(
            status="success",
            message="Panggilan Drive API berhasil!",
            first_10_files=[DriveFile(id=f["id"], name=f["name"], type=f["mimeType"]) for f in files],
        )
    except Exception as e:
        return TestDriveResponse(status="error", message=f"Gagal memanggil Drive API: {e}")

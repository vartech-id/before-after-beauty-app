import base64
import io
from pathlib import Path

import requests
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from PIL import Image

from backend.config import AFTER_DIR, RESULT_DIR, API_BASE_URL, STATIC_DIR
from backend.models.presets import VALID_PRESETS
from backend.services.beautify import beautify_image
from backend.services.storage import save_image_lossless

router = APIRouter(prefix="/api")


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

    # Simpan hasil filter ke folder after & result (lossless PNG, kualitas asli)
    after_filename = save_image_lossless(out_img, AFTER_DIR, prefix="after")
    result_filename = save_image_lossless(out_img, RESULT_DIR, prefix="result")

    after_url = f"{API_BASE_URL.rstrip('/')}/static/after/{after_filename}"
    result_url = f"{API_BASE_URL.rstrip('/')}/static/result/{result_filename}"

    buffer = io.BytesIO()
    out_img.save(buffer, format="JPEG", quality=95)
    buffer.seek(0)

    return Response(
        content=buffer.read(),
        media_type="image/jpeg",
        headers={
          "X-After-Url": after_url,
          "X-Result-Url": result_url,
          "Access-Control-Expose-Headers": "X-After-Url, X-Result-Url",
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

    filename = save_image_lossless(canvas, RESULT_DIR, prefix="result")
    result_url = f"{API_BASE_URL.rstrip('/')}/static/result/{filename}"

    return JSONResponse({"result_url": result_url})

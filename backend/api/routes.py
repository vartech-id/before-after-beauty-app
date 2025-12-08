import io
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image

from backend.config import AFTER_DIR, RESULT_DIR, API_BASE_URL
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
        },
    )

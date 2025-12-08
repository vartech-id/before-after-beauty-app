# backend/main.py
import asyncio
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel

from backend.config import FRONTEND_ORIGINS, STATIC_DIR
from backend.api.camera import router as camera_router
from backend.api.routes import router as beauty_router  # /api endpoints
from backend.services.watcher_service import (
    set_main_async_loop,
    start_local_watcher,
    stop_local_watcher,
)

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in FRONTEND_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve /static -> backend/static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Router
app.include_router(camera_router)  # /api/camera/...
app.include_router(beauty_router)  # /api/beauty, /api/render-result, etc.


@app.on_event("startup")
async def on_startup():
    loop = asyncio.get_event_loop()
    set_main_async_loop(loop)
    start_local_watcher()


@app.on_event("shutdown")
async def on_shutdown():
    stop_local_watcher()


@app.get("/health")
def health_check():
    return {"status": "ok"}


class RenderRequest(BaseModel):
    photo_path: str  # path foto dari kamera
    template_name: str  # misal "template1.json"


@app.post("/render")
def render(req: RenderRequest):
    tpl_path = BASE_DIR / "templates" / req.template_name
    with open(tpl_path, "r", encoding="utf-8") as f:
        tpl = json.load(f)

    canvas_w = tpl["canvas"]["width"]
    canvas_h = tpl["canvas"]["height"]
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 255))

    photo = Image.open(BASE_DIR / req.photo_path).convert("RGBA")

    # contoh: cuma pakai 1 slot kamera
    slot = tpl["camera_slots"][0]
    x = int(slot["x_rel"] * canvas_w)
    y = int(slot["y_rel"] * canvas_h)
    w = int(slot["w_rel"] * canvas_w)
    h = int(slot["h_rel"] * canvas_h)

    photo_resized = photo.resize((w, h), Image.LANCZOS)
    canvas.alpha_composite(photo_resized, dest=(x, y))

    # TODO: loop overlays di tpl["overlays"] kalau ada

    out_dir = BASE_DIR / "outputs"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "result.png"
    canvas.save(out_path, format="PNG")

    return {"status": "ok", "output": str(out_path.relative_to(BASE_DIR))}

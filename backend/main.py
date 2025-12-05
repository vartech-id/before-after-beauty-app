# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import FRONTEND_ORIGINS, STATIC_DIR
from backend.api.camera import router as camera_router
from backend.api.routes import router as beauty_router   # 🔥 tambahkan ini

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in FRONTEND_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve /static -> backend/static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 🔥 daftar kedua router
app.include_router(camera_router)   # /api/camera/...
app.include_router(beauty_router)   # /api/beauty

@app.get("/health")
def health_check():
    return {"status": "ok"}

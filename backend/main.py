# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import FRONTEND_ORIGINS, STATIC_DIR
from backend.api.camera import router as camera_router

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

app.include_router(camera_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

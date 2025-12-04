# backend/models/camera.py
from pydantic import BaseModel


class CaptureResponse(BaseModel):
    """
    Response standar untuk endpoint /api/camera/capture.

    Kita sengaja cuma kirim satu field:
    - photo_url: URL absolute yang bisa langsung dipakai <img src="...">
    """
    photo_url: str

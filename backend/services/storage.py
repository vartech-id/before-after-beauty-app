from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image


def save_image_lossless(
    image: Image.Image,
    directory: Path,
    prefix: str = "img",
    filename: Optional[str] = None,
) -> str:
    """
    Simpan image ke directory dalam format PNG tanpa kompresi yang
    menurunkan kualitas. Mengembalikan nama file saja (bukan path penuh).
    """
    directory.mkdir(parents=True, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        filename = f"{prefix}_{timestamp}.png"

    path = directory / filename
    image.save(path, format="PNG", compress_level=0)  # lossless
    return filename

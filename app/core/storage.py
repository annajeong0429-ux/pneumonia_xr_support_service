import uuid
from pathlib import Path

from fastapi import UploadFile

MEDIA_DIR = Path(__file__).resolve().parent.parent.parent / "media"
XRAY_SUBDIR = "xray"


async def save_xray_image(file: UploadFile) -> str:
    target_dir = MEDIA_DIR / XRAY_SUBDIR
    target_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = target_dir / filename

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return f"/media/{XRAY_SUBDIR}/{filename}"

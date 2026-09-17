
from io import BytesIO

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.config import MAX_IMAGE_SIZE_BYTES
from app.models.vision import ImageMetadata


SUPPORTED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


async def validate_image(
    image: UploadFile,
) -> tuple[bytes, ImageMetadata]:

    if not image:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "MISSING_IMAGE",
                "message": "Image file is required.",
            },
        )

    if image.content_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(
            status_code=415,
            detail={
                "success": False,
                "status_code": 415,
                "error": "UNSUPPORTED_IMAGE_TYPE",
                "message": (
                    "Supported image types are JPG, JPEG, PNG and WEBP."
                ),
            },
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "EMPTY_IMAGE",
                "message": "Uploaded image is empty.",
            },
        )

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail={
                "success": False,
                "status_code": 413,
                "error": "IMAGE_TOO_LARGE",
                "message": "Image exceeds the configured size limit.",
            },
        )

    try:
        with Image.open(BytesIO(image_bytes)) as img:
            img.verify()

        with Image.open(BytesIO(image_bytes)) as img:
            width, height = img.size

    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "status_code": 400,
                "error": "INVALID_IMAGE",
                "message": "Uploaded file is not a valid image.",
            },
        )

    metadata = ImageMetadata(
        file_name=image.filename or "unknown",
        content_type=image.content_type,
        size_bytes=len(image_bytes),
        width=width,
        height=height,
    )

    return image_bytes, metadata
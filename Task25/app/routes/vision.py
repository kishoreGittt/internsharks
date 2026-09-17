from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.vision_service import (
    call_vision_model,
    compare_images_with_model,
)


router = APIRouter(
    prefix="/vision",
    tags=["Vision"],
)


AnalysisType = Literal[
    "general",
    "document",
    "product",
    "ui",
]


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


@router.post("/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    prompt: str = Form("Describe this image"),
    analysis_type: AnalysisType = Form("general"),
):
    """
    Analyze one uploaded image.
    """

    content_type = image.content_type or ""

    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "UNSUPPORTED_IMAGE_TYPE",
                "message": (
                    "Unsupported image type. "
                    "Use JPEG, PNG, WEBP, or GIF."
                ),
            },
        )

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "EMPTY_IMAGE",
                "message": "Uploaded image is empty",
            },
        )

    return await call_vision_model(
        image_bytes=image_bytes,
        content_type=content_type,
        file_name=image.filename or "uploaded_image",
        prompt=prompt,
        analysis_type=analysis_type,
    )


@router.post("/compare")
async def compare_images(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    prompt: str = Form(
        "Compare these two images and describe their visible differences."
    ),
):
    """
    Compare two uploaded images.
    """

    image1_content_type = image1.content_type or ""
    image2_content_type = image2.content_type or ""

    if image1_content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "UNSUPPORTED_IMAGE_TYPE",
                "message": "Unsupported image type for image1",
            },
        )

    if image2_content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "UNSUPPORTED_IMAGE_TYPE",
                "message": "Unsupported image type for image2",
            },
        )

    image1_bytes = await image1.read()
    image2_bytes = await image2.read()

    if not image1_bytes:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "EMPTY_IMAGE",
                "message": "First image is empty",
            },
        )

    if not image2_bytes:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "EMPTY_IMAGE",
                "message": "Second image is empty",
            },
        )

    return await compare_images_with_model(
        image1_bytes=image1_bytes,
        image1_content_type=image1_content_type,
        image1_file_name=image1.filename or "image1",
        image2_bytes=image2_bytes,
        image2_content_type=image2_content_type,
        image2_file_name=image2.filename or "image2",
        prompt=prompt,
    )
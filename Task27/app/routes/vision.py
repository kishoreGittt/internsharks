from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.auth.dependencies import get_current_user
from app.services.vision_service import analyze_image


router = APIRouter(
    prefix="/vision",
    tags=["Vision"]
)


@router.post("/analyze")
async def analyze_vision(
    file: UploadFile = File(...),
    prompt: str = Form(
        "Describe this image and explain the important information visible in it."
    ),
    current_user: dict = Depends(get_current_user)
):
    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "status_code": 400,
                    "error": "INVALID_FILE",
                    "message": "Image file is required."
                }
            )

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp"
        }

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "status_code": 400,
                    "error": "UNSUPPORTED_IMAGE",
                    "message": "Only JPEG, PNG, and WEBP images are supported."
                }
            )

        image_bytes = await file.read()

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "status_code": 400,
                    "error": "EMPTY_FILE",
                    "message": "Uploaded image is empty."
                }
            )

        if not prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "status_code": 400,
                    "error": "INVALID_PROMPT",
                    "message": "Prompt cannot be empty."
                }
            )

        result = await analyze_image(
            image_bytes,
            file.content_type,
            prompt
        )

        return {
            "success": True,
            "status_code": 200,
            "data": result
        }

    except HTTPException:
        raise

    except Exception as error:
        print("\n==========================================")
        print("            VISION ERROR")
        print("==========================================")
        print(f"Error type : {type(error).__name__}")
        print(f"Error      : {error}")
        print("==========================================\n")

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error": "VISION_REQUEST_FAILED",
                "message": "Vision request failed safely."
            }
        )
from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    Form,
    HTTPException
)

from app.auth.dependencies import (
    get_current_user
)

from app.services.vision_service import (
    analyze_image
)


router = APIRouter(
    prefix="/vision",
    tags=["Vision"]
)


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


@router.post(
    "/analyze"
)
async def analyze(

    file: UploadFile = File(...),

    prompt: str = Form(
        "Describe this image."
    ),

    current_user: dict = Depends(
        get_current_user
    )

):

    try:

        if file.content_type not in (
            ALLOWED_IMAGE_TYPES
        ):

            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "status_code": 400,
                    "error": "INVALID_IMAGE_TYPE",
                    "message": (
                        "Only JPEG, PNG and WEBP "
                        "images are supported."
                    )
                }
            )

        image_bytes = await file.read()

        if not image_bytes:

            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "status_code": 400,
                    "error": "EMPTY_IMAGE",
                    "message": (
                        "Uploaded image is empty."
                    )
                }
            )

        result = await analyze_image(
            image_bytes=image_bytes,
            content_type=file.content_type,
            prompt=prompt
        )

        return {

            "success": True,

            "status_code": 200,

            "data": {

                "answer":
                    result["answer"],

                "model":
                    result["model"]
            }
        }

    except HTTPException:

        raise

    except Exception as error:

        print(
            f"VISION ERROR: "
            f"{type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "status_code": 502,
                "error":
                    "VISION_REQUEST_FAILED",
                "message":
                    "Vision request failed safely."
            }
        )
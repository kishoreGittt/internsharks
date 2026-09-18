from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.auth.dependencies import (
    get_current_user
)

from app.storage.mongodb import (
    traces_collection
)


router = APIRouter(
    prefix="/observability",
    tags=["Observability"]
)


@router.get(
    "/traces/{trace_id}"
)
async def get_trace(

    trace_id: str,

    current_user: dict = Depends(
        get_current_user
    )
):

    trace = await traces_collection.find_one(

        {
            "trace_id": trace_id,

            "owner_id":
                current_user["user_id"]
        },

        {
            "_id": 0
        }
    )

    if not trace:

        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "status_code": 404,
                "error":
                    "TRACE_NOT_FOUND",
                "message":
                    "Trace not found."
            }
        )

    return {
        "success": True,
        "status_code": 200,
        "trace": trace
    }
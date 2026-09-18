from fastapi import (
    APIRouter,
    Depends
)

from app.auth.dependencies import (
    get_current_user
)

from app.evals.runner import (
    run_evaluation
)


router = APIRouter(
    prefix="/eval",
    tags=["Evaluation"]
)


@router.post(
    "/run"
)
async def run_eval(

    current_user: dict = Depends(
        get_current_user
    )
):

    result = await run_evaluation()

    return {

        "success": True,

        "status_code": 200,

        "run_id":
            f"eval_{current_user['user_id']}",

        **result
    }
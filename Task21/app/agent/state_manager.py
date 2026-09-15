from app.storage.run_repository import (
    get_run,
    update_run
)


async def load_state(run_id: str):

    run = await get_run(run_id)

    if not run:
        raise ValueError(
            "Agent run not found"
        )

    return run


async def save_pending_action(
    run_id: str,
    action: dict
):

    await update_run(
        run_id,
        {
            "status": "waiting_for_approval",
            "pending_action": action
        }
    )


async def clear_pending_action(run_id: str):

    await update_run(
        run_id,
        {
            "pending_action": None
        }
    )
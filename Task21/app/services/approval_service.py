from fastapi import HTTPException

from app.storage.action_repository import (
    get_action_for_run,
    update_action,
)

from app.storage.run_repository import (
    get_run,
    update_run,
    append_trace,
)

from app.agent.runner import execute_tool


async def process_approval(
    run_id: str,
    action_id: str,
    approved: bool,
):
    run = await get_run(run_id)

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Agent run not found",
        )

    action = await get_action_for_run(
        run_id,
        action_id,
    )

    if not action:
        raise HTTPException(
            status_code=404,
            detail="Action not found",
        )

    current_status = action.get("status")

    # Prevent duplicate approval execution
    if current_status in ["executed", "rejected"]:
        return {
            "success": True,
            "message": "This action was already processed",
            "run_id": run_id,
            "action_id": action_id,
            "action_status": current_status,
            "run_status": run.get("status"),
        }

    if not approved:
        await update_action(
            action_id,
            {
                "status": "rejected",
                "approval": "rejected",
            },
        )

        await append_trace(
            run_id,
            {
                "event": "action_rejected",
                "action_id": action_id,
                "tool": action.get("tool"),
            },
        )

        updated_run = await update_run(
            run_id,
            {
                "status": "rejected",
                "pending_action": None,
            },
        )

        return {
            "success": True,
            "message": "Action rejected successfully",
            "run_id": run_id,
            "action_id": action_id,
            "action_status": "rejected",
            "run_status": updated_run.get("status"),
        }

    # Mark approved before execution to avoid duplicate execution
    await update_action(
        action_id,
        {
            "status": "approved",
            "approval": "approved",
        },
    )

    await append_trace(
        run_id,
        {
            "event": "action_approved",
            "action_id": action_id,
            "tool": action.get("tool"),
        },
    )

    tool_name = action.get("tool")
    arguments = action.get("arguments", {})

    try:
        tool_result = await execute_tool(
            tool_name,
            arguments,
        )

        await update_action(
            action_id,
            {
                "status": "executed",
                "result": tool_result,
            },
        )

        await append_trace(
            run_id,
            {
                "event": "action_executed",
                "action_id": action_id,
                "tool": tool_name,
            },
        )

        updated_run = await update_run(
            run_id,
            {
                "status": "completed",
                "pending_action": None,
                "last_result": tool_result,
            },
        )

        return {
            "success": True,
            "message": "Action approved and executed successfully",
            "run_id": run_id,
            "action_id": action_id,
            "action_status": "executed",
            "run_status": updated_run.get("status"),
            "result": tool_result,
        }

    except Exception as error:
        await update_action(
            action_id,
            {
                "status": "failed",
                "error": str(error),
            },
        )

        await update_run(
            run_id,
            {
                "status": "failed",
                "pending_action": None,
            },
        )

        raise HTTPException(
            status_code=500,
            detail="Action execution failed",
        )
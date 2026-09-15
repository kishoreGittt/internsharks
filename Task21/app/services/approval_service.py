from app.agent.registry import get_tool
from app.agent.runner import execute_tool

from app.storage.run_repository import (
    get_run,
    update_run,
    append_trace
)

from app.storage.action_repository import (
    get_action,
    update_action,
    get_action_for_run
)


async def process_approval(
    run_id: str,
    action_id: str,
    approved: bool
):

    run = await get_run(run_id)

    if not run:
        raise ValueError(
            "Agent run not found"
        )

    action = await get_action_for_run(
        run_id,
        action_id
    )

    if not action:
        raise ValueError(
            "Action not found"
        )

    # Duplicate protection
    if action["status"] == "executed":

        return {
            "message": "Action already executed",
            "executed": False,
            "run": run
        }

    if action["status"] == "rejected":

        return {
            "message": "Action already rejected",
            "executed": False,
            "run": run
        }

    if action["status"] != "pending":

        raise ValueError(
            "Action cannot be approved in current state"
        )

    if not approved:

        await update_action(
            action_id,
            {
                "status": "rejected"
            }
        )

        await append_trace(
            run_id,
            {
                "step": run["step_count"],
                "type": "approval",
                "action_id": action_id,
                "tool": action["tool"],
                "status": "rejected"
            }
        )

        await update_run(
            run_id,
            {
                "status": "rejected",
                "pending_action": None
            }
        )

        return {
            "message": "Action rejected",
            "executed": False,
            "run": await get_run(run_id)
        }

    # Revalidate before execution
    tool = get_tool(action["tool"])

    if not tool:

        raise ValueError(
            "Unknown tool"
        )

    try:

        result = await execute_tool(
            run_id,
            action["tool"],
            action["arguments"]
        )

    except Exception as exc:

        await update_action(
            action_id,
            {
                "status": "approved",
                "execution_error": str(exc)
            }
        )

        await update_run(
            run_id,
            {
                "status": "failed",
                "pending_action": None
            }
        )

        raise ValueError(
            "Action failed during execution"
        )

    await update_action(
        action_id,
        {
            "status": "executed"
        }
    )

    await update_run(
        run_id,
        {
            "status": "completed",
            "pending_action": None
        }
    )

    return {
        "message": "Action approved and executed",
        "executed": True,
        "result": result,
        "run": await get_run(run_id)
    }
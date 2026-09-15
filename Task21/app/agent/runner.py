import uuid
from datetime import datetime, timezone

from app.config import MAX_AGENT_STEPS

from app.agent.registry import get_tool

from app.storage.run_repository import (
    create_run,
    get_run,
    update_run,
    append_trace,
    increment_step
)

from app.storage.action_repository import (
    create_action
)


def new_id(prefix: str):

    return f"{prefix}_{uuid.uuid4().hex[:12]}"


async def create_agent_run(goal: str):

    run_id = new_id("run")

    run = {
        "run_id": run_id,
        "goal": goal,
        "status": "running",
        "step_count": 0,
        "messages": [],
        "pending_action": None,
        "execution_trace": [],
        "created_at": datetime.now(
            timezone.utc
        ).isoformat()
    }

    await create_run(run)

    # Simple goal planner
    action = build_action_from_goal(goal)

    if action is None:

        await update_run(
            run_id,
            {
                "status": "failed"
            }
        )

        return await get_run(run_id)

    return await process_action(
        run_id,
        action
    )


def build_action_from_goal(goal: str):

    goal_lower = goal.lower()

    if "create a project" in goal_lower:

        name = extract_project_name(goal)

        return {
            "tool": "create_project",
            "arguments": {
                "name": name,
                "description": ""
            }
        }

    if "find" in goal_lower and "employee" in goal_lower:

        name = extract_employee_name(goal)

        return {
            "tool": "find_employee",
            "arguments": {
                "name": name
            }
        }

    return None


def extract_project_name(goal: str):

    marker = "called "

    lower = goal.lower()

    if marker in lower:

        index = lower.index(marker)

        value = goal[
            index + len(marker):
        ]

        return value.split(",")[0].strip()

    return "New Project"


def extract_employee_name(goal: str):

    words = goal.split()

    for index, word in enumerate(words):

        if word.lower() == "employee" and index > 0:

            return words[index - 1]

    return "Arun"


async def process_action(
    run_id: str,
    action: dict
):

    run = await get_run(run_id)

    if not run:
        raise ValueError(
            "Agent run not found"
        )

    if run["step_count"] >= MAX_AGENT_STEPS:

        await update_run(
            run_id,
            {
                "status": "failed"
            }
        )

        return await get_run(run_id)

    tool_name = action["tool"]

    tool = get_tool(tool_name)

    if not tool:

        await update_run(
            run_id,
            {
                "status": "failed"
            }
        )

        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

    await increment_step(run_id)

    if tool["requires_approval"]:

        action_id = new_id("action")

        pending_action = {
            "action_id": action_id,
            "tool": tool_name,
            "arguments": action["arguments"]
        }

        approval = {
            "action_id": action_id,
            "run_id": run_id,
            "tool": tool_name,
            "arguments": action["arguments"],
            "status": "pending"
        }

        await create_action(approval)

        await update_run(
            run_id,
            {
                "status": "waiting_for_approval",
                "pending_action": pending_action
            }
        )

        await append_trace(
            run_id,
            {
                "step": run["step_count"] + 1,
                "type": "approval_required",
                "tool": tool_name,
                "action_id": action_id,
                "status": "waiting"
            }
        )

        return await get_run(run_id)

    result = await execute_tool(
        run_id,
        tool_name,
        action["arguments"]
    )

    await update_run(
        run_id,
        {
            "status": "completed",
            "pending_action": None
        }
    )

    return {
        "run": await get_run(run_id),
        "result": result
    }


async def execute_tool(
    run_id: str,
    tool_name: str,
    arguments: dict
):

    tool = get_tool(tool_name)

    if not tool:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

    function = tool["function"]

    result = await function(
        **arguments
    )

    run = await get_run(run_id)

    await append_trace(
        run_id,
        {
            "step": run["step_count"],
            "type": "tool_execution",
            "tool": tool_name,
            "status": "success"
        }
    )

    return result
import pytest

from app.tools.project_tools import (
    UpdateTaskStatusArgs
)


def test_invalid_tool_status():

    with pytest.raises(
        Exception
    ):

        UpdateTaskStatusArgs.model_validate(

            {
                "project_id":
                    "project-1",

                "task_id":
                    "task-1",

                "status":
                    "wrong-status"
            }
        )
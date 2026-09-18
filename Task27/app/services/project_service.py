import uuid

from app.storage.repositories.project_repository import (
    create_project
)


async def create_demo_project(
    owner_id: str
):

    project_id = str(
        uuid.uuid4()
    )

    project = {

        "project_id": project_id,

        "owner_id": owner_id,

        "name": "Project Nova",

        "description":
            "AI knowledge and operations project.",

        "manager": {
            "name": "Arun",
            "role": "Project Manager"
        },

        "members": [
            {
                "user_id": "member_001",
                "name": "Arun",
                "role": "Project Manager"
            },
            {
                "user_id": "member_002",
                "name": "Priya",
                "role": "Backend Engineer"
            },
            {
                "user_id": "member_003",
                "name": "Kumar",
                "role": "AI Engineer"
            }
        ],

        "tasks": [
            {
                "task_id": "task_001",
                "title": "Implement authentication",
                "description":
                    "Implement JWT authentication.",
                "status": "completed"
            },
            {
                "task_id": "task_002",
                "title": "Build RAG pipeline",
                "description":
                    "Implement document retrieval.",
                "status": "in_progress"
            },
            {
                "task_id": "task_003",
                "title": "Write production tests",
                "description":
                    "Add automated tests.",
                "status": "pending"
            }
        ]
    }

    return await create_project(
        project
    )
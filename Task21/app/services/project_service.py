from app.storage.database import get_connection


class ProjectService:

    def find_employee(self, name: str):
        connection = get_connection()

        row = connection.execute(
            """
            SELECT id, name
            FROM employees
            WHERE LOWER(name) = LOWER(?)
            """,
            (name,),
        ).fetchone()

        connection.close()

        if not row:
            return {
                "success": False,
                "error": "Employee not found"
            }

        return {
            "success": True,
            "employee": {
                "id": row["id"],
                "name": row["name"]
            }
        }

    def get_project(self, project_id: int):
        connection = get_connection()

        row = connection.execute(
            """
            SELECT id, name
            FROM projects
            WHERE id = ?
            """,
            (project_id,),
        ).fetchone()

        connection.close()

        if not row:
            return {
                "success": False,
                "error": "Project not found"
            }

        return {
            "success": True,
            "project": {
                "id": row["id"],
                "name": row["name"]
            }
        }

    def list_projects(self):
        connection = get_connection()

        rows = connection.execute(
            """
            SELECT id, name
            FROM projects
            ORDER BY id
            """
        ).fetchall()

        connection.close()

        return {
            "success": True,
            "projects": [
                {
                    "id": row["id"],
                    "name": row["name"]
                }
                for row in rows
            ]
        }

    def get_project_tasks(self, project_id: int):
        connection = get_connection()

        rows = connection.execute(
            """
            SELECT
                id,
                project_id,
                title,
                description,
                priority,
                status,
                assigned_to
            FROM tasks
            WHERE project_id = ?
            ORDER BY id
            """,
            (project_id,),
        ).fetchall()

        connection.close()

        return {
            "success": True,
            "tasks": [dict(row) for row in rows]
        }

    def get_task(self, task_id: int):
        connection = get_connection()

        row = connection.execute(
            """
            SELECT
                id,
                project_id,
                title,
                description,
                priority,
                status,
                assigned_to
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

        connection.close()

        if not row:
            return {
                "success": False,
                "error": "Task not found"
            }

        return {
            "success": True,
            "task": dict(row)
        }

    # -------------------------
    # WRITE OPERATIONS
    # -------------------------

    def create_project(self, name: str):
        connection = get_connection()

        existing = connection.execute(
            """
            SELECT id, name
            FROM projects
            WHERE LOWER(name) = LOWER(?)
            """,
            (name,),
        ).fetchone()

        if existing:
            connection.close()

            return {
                "success": False,
                "error": "Project already exists",
                "project": {
                    "id": existing["id"],
                    "name": existing["name"]
                }
            }

        cursor = connection.execute(
            """
            INSERT INTO projects(name)
            VALUES (?)
            """,
            (name,),
        )

        project_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return {
            "success": True,
            "project": {
                "id": project_id,
                "name": name
            }
        }

    def add_project_member(
        self,
        project_id: int,
        employee_id: int
    ):
        connection = get_connection()

        project = connection.execute(
            "SELECT id FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()

        if not project:
            connection.close()

            return {
                "success": False,
                "error": "Project not found"
            }

        employee = connection.execute(
            "SELECT id, name FROM employees WHERE id = ?",
            (employee_id,),
        ).fetchone()

        if not employee:
            connection.close()

            return {
                "success": False,
                "error": "Employee not found"
            }

        existing = connection.execute(
            """
            SELECT *
            FROM project_members
            WHERE project_id = ?
            AND employee_id = ?
            """,
            (
                project_id,
                employee_id,
            ),
        ).fetchone()

        if existing:
            connection.close()

            return {
                "success": False,
                "error": "Employee is already a project member"
            }

        connection.execute(
            """
            INSERT INTO project_members
            (
                project_id,
                employee_id
            )
            VALUES (?, ?)
            """,
            (
                project_id,
                employee_id,
            ),
        )

        connection.commit()
        connection.close()

        return {
            "success": True,
            "message": "Employee added to project"
        }

    def create_project_task(
        self,
        project_id: int,
        title: str,
        description: str = None,
        priority: str = "medium",
        assigned_to: int = None,
    ):
        if priority not in {
            "low",
            "medium",
            "high"
        }:
            return {
                "success": False,
                "error": "Invalid priority"
            }

        connection = get_connection()

        project = connection.execute(
            "SELECT id FROM projects WHERE id = ?",
            (project_id,),
        ).fetchone()

        if not project:
            connection.close()

            return {
                "success": False,
                "error": "Project not found"
            }

        if assigned_to is not None:
            employee = connection.execute(
                "SELECT id FROM employees WHERE id = ?",
                (assigned_to,),
            ).fetchone()

            if not employee:
                connection.close()

                return {
                    "success": False,
                    "error": "Assigned employee not found"
                }

        cursor = connection.execute(
            """
            INSERT INTO tasks
            (
                project_id,
                title,
                description,
                priority,
                status,
                assigned_to
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                title,
                description,
                priority,
                "todo",
                assigned_to,
            ),
        )

        task_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return {
            "success": True,
            "task": {
                "id": task_id,
                "project_id": project_id,
                "title": title,
                "description": description,
                "priority": priority,
                "status": "todo",
                "assigned_to": assigned_to,
            }
        }

    def update_task_status(
        self,
        task_id: int,
        status: str
    ):
        allowed = {
            "todo",
            "in_progress",
            "completed"
        }

        if status not in allowed:
            return {
                "success": False,
                "error": "Invalid task status"
            }

        connection = get_connection()

        task = connection.execute(
            "SELECT id FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if not task:
            connection.close()

            return {
                "success": False,
                "error": "Task not found"
            }

        connection.execute(
            """
            UPDATE tasks
            SET status = ?
            WHERE id = ?
            """,
            (
                status,
                task_id,
            ),
        )

        connection.commit()
        connection.close()

        return {
            "success": True,
            "message": "Task status updated",
            "task_id": task_id,
            "status": status
        }

    def delete_project_task(self, task_id: int):
        connection = get_connection()

        task = connection.execute(
            """
            SELECT id, title
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

        if not task:
            connection.close()

            return {
                "success": False,
                "error": "Task not found"
            }

        connection.execute(
            """
            DELETE FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        connection.commit()
        connection.close()

        return {
            "success": True,
            "message": "Task deleted",
            "task_id": task_id
        }
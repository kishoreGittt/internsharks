from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from app.storage.database import evaluation_collection


class EvaluationRepository:
    """
    MongoDB repository for Task23 evaluation runs.
    """

    def __init__(self, collection: Collection) -> None:
        self.collection = collection
        self._create_indexes()

    def _create_indexes(self) -> None:
        """
        Creates MongoDB indexes safely.
        """

        try:
            self.collection.create_index(
                "run_id",
                unique=True,
            )

            self.collection.create_index(
                "created_at",
            )

        except PyMongoError:
            # MongoDB may be unavailable during startup.
            pass

    def create_run(
        self,
        run_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Saves an evaluation run.

        If run_id is missing, it is generated automatically.
        """

        data = dict(run_data)

        # Generate run_id automatically when missing
        if not data.get("run_id"):
            data["run_id"] = (
                f"run_{uuid4().hex}"
            )

        # Add creation timestamp automatically
        if not data.get("created_at"):
            data["created_at"] = (
                datetime.now(timezone.utc).isoformat()
            )

        self.collection.insert_one(data)

        return self._serialize(data)

    def get_run(
        self,
        run_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Gets one evaluation run by run_id.
        """

        document = self.collection.find_one(
            {"run_id": run_id},
            {"_id": 0},
        )

        if document is None:
            return None

        return self._serialize(document)

    def get_failures(
        self,
        run_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Gets failed evaluation cases.
        """

        run = self.get_run(run_id)

        if run is None:
            return []

        failures = run.get("failures")

        if isinstance(failures, list):
            return failures

        results = run.get("results", [])

        if not isinstance(results, list):
            return []

        return [
            result
            for result in results
            if isinstance(result, dict)
            and result.get("passed") is False
        ]

    def list_runs(
        self,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Returns recent evaluation runs.
        """

        limit = max(1, min(limit, 100))

        documents = (
            self.collection
            .find({}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )

        return [
            self._serialize(document)
            for document in documents
        ]

    def delete_run(
        self,
        run_id: str,
    ) -> bool:
        """
        Deletes an evaluation run.
        """

        result = self.collection.delete_one(
            {"run_id": run_id}
        )

        return result.deleted_count > 0

    @staticmethod
    def _serialize(
        document: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Converts MongoDB data into JSON-friendly data.
        """

        data = dict(document)

        data.pop("_id", None)

        created_at = data.get("created_at")

        if isinstance(created_at, datetime):
            data["created_at"] = created_at.isoformat()

        return data


# =========================================================
# Global repository
# =========================================================

evaluation_repository = EvaluationRepository(
    evaluation_collection
)


# =========================================================
# Compatibility helper functions
# =========================================================

def save_run(
    run_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Saves an evaluation run.
    """

    return evaluation_repository.create_run(
        run_data
    )


def get_run(
    run_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Gets an evaluation run.
    """

    return evaluation_repository.get_run(
        run_id
    )


def get_failures(
    run_id: str,
) -> List[Dict[str, Any]]:
    """
    Gets failed cases for a run.
    """

    return evaluation_repository.get_failures(
        run_id
    )


def list_runs(
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Lists recent evaluation runs.
    """

    return evaluation_repository.list_runs(
        limit
    )


def delete_run(
    run_id: str,
) -> bool:
    """
    Deletes an evaluation run.
    """

    return evaluation_repository.delete_run(
        run_id
    )
from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.config import settings


class MongoDatabase:
    """
    MongoDB connection manager for Task23.

    This class:
    - Creates the MongoDB client
    - Selects the database
    - Selects the collection
    - Checks MongoDB availability
    - Closes the connection safely
    """

    def __init__(self) -> None:
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.collection: Optional[Collection] = None

        self.connect()

    def connect(self) -> None:
        """
        Creates the MongoDB connection objects.

        MongoClient does not immediately contact MongoDB.
        The real connection is checked using check_connection().
        """

        self.client = MongoClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
        )

        self.database = self.client[settings.mongodb_database]

        self.collection = self.database[
            settings.mongodb_collection
        ]

    def check_connection(self) -> bool:
        """
        Checks whether MongoDB Server is reachable.

        Returns:
            True  -> MongoDB is available
            False -> MongoDB is unavailable
        """

        if self.client is None:
            return False

        try:
            self.client.admin.command("ping")
            return True

        except PyMongoError:
            return False

        except Exception:
            return False

    def get_database(self) -> Database:
        """
        Returns the selected MongoDB database.
        """

        if self.database is None:
            raise RuntimeError("MongoDB database is not initialized.")

        return self.database

    def get_collection(self) -> Collection:
        """
        Returns the selected MongoDB collection.
        """

        if self.collection is None:
            raise RuntimeError("MongoDB collection is not initialized.")

        return self.collection

    def close(self) -> None:
        """
        Closes the MongoDB client safely.
        """

        if self.client is not None:
            self.client.close()


mongo_database = MongoDatabase()

db = mongo_database.get_database()

evaluation_collection = mongo_database.get_collection()
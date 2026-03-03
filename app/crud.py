from typing import Iterable
from bson import ObjectId

from pymongo.collection import Collection


def list_items(collection: Collection) -> Iterable[dict]:
    return collection.find()


def create_item(collection: Collection, payload: dict) -> str:
    result = collection.insert_one(payload)
    return str(result.inserted_id)


def remove_item(collection: Collection, item_id: str) -> int:
    return collection.delete_one({"_id": ObjectId(item_id)}).deleted_count

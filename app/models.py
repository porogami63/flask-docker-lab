from bson import ObjectId


def format_item(document: dict) -> dict:
    return {
        "id": str(document.get("_id", "")),
        "name": document.get("name", ""),
        "description": document.get("description", ""),
    }

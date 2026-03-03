from flask import Flask, jsonify, request, abort, send_from_directory
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.errors import InvalidId
import os

from .crud import list_items, create_item, remove_item
from .models import format_item

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), os.pardir, ".env"))

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set in the environment")

MONGO_DB = os.getenv("MONGO_DB", "FlaskApp-Docker")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
items_collection = db.items

# Determine the static folder path - handle both local and Docker environments
app_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(app_dir)
public_dir = os.path.join(parent_dir, "public")

# Fallback to common Docker paths
if not os.path.exists(public_dir):
    public_dir = os.path.join("/app", "public")
if not os.path.exists(public_dir):
    public_dir = os.getcwd()

app = Flask(__name__, static_folder=public_dir, static_url_path="/static")


@app.route("/")
def serve_index():
    return send_from_directory(public_dir, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    filepath = os.path.join(public_dir, filename)
    if os.path.isfile(filepath):
        return send_from_directory(public_dir, filename)
    return send_from_directory(public_dir, "index.html")


@app.route("/items", methods=["GET"])
def get_items():
    docs = list_items(items_collection)
    return jsonify([format_item(doc) for doc in docs])


@app.route("/items", methods=["POST"])
def post_item():
    payload = request.get_json()
    if not payload or "name" not in payload:
        abort(400, description="Request must include a 'name'")
    item = {
        "name": payload["name"],
        "description": payload.get("description", ""),
    }
    inserted_id = create_item(items_collection, item)
    return jsonify({"inserted_id": inserted_id}), 201


@app.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id: str):
    try:
        deleted_count = remove_item(items_collection, item_id)
    except InvalidId:
        abort(400, description="Invalid item id")
    if deleted_count:
        return jsonify({"status": "deleted"})
    abort(404, description="Item not found")


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

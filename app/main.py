from flask import Flask, jsonify, request, abort, send_from_directory
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.errors import InvalidId
import os
import logging

from .crud import list_items, create_item, remove_item
from .models import format_item

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), os.pardir, ".env"))

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "FlaskApp-Docker")

# Database connection variables - initialized on first use
client = None
db = None
items_collection = None

def get_db():
    """Lazy load database connection"""
    global client, db, items_collection
    if client is None:
        if not MONGO_URI:
            logger.error("MONGO_URI is not set")
            raise RuntimeError("MONGO_URI is not set in the environment")
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            client.server_info()  # Test connection
            db = client[MONGO_DB]
            items_collection = db.items
            logger.info("MongoDB connected successfully")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    return items_collection

# Determine the static folder path
app_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(app_dir)
public_dir = os.path.join(parent_dir, "public")

# Fallback paths for Docker
if not os.path.exists(public_dir):
    public_dir = "/app/public"
if not os.path.exists(public_dir):
    public_dir = os.getcwd()

logger.info(f"Static files directory: {public_dir}")
logger.info(f"Static files exist: {os.path.exists(public_dir)}")

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
    try:
        collection = get_db()
        docs = list_items(collection)
        return jsonify([format_item(doc) for doc in docs])
    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/items", methods=["POST"])
def post_item():
    try:
        payload = request.get_json()
        if not payload or "name" not in payload:
            abort(400, description="Request must include a 'name'")
        item = {
            "name": payload["name"],
            "description": payload.get("description", ""),
        }
        collection = get_db()
        inserted_id = create_item(collection, item)
        return jsonify({"inserted_id": inserted_id}), 201
    except Exception as e:
        logger.error(f"Error creating item: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id: str):
    try:
        collection = get_db()
        deleted_count = remove_item(collection, item_id)
    except InvalidId:
        abort(400, description="Invalid item id")
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        return jsonify({"error": str(e)}), 500
    if deleted_count:
        return jsonify({"status": "deleted"})
    abort(404, description="Item not found")


@app.route("/health", methods=["GET"])
def health_check():
    try:
        collection = get_db()
        return jsonify({"status": "ok", "database": "connected"})
    except:
        return jsonify({"status": "ok", "database": "disconnected"}), 200


@app.errorhandler(404)
def not_found(error):
    """Serve index.html for all unmatched routes (SPA fallback)"""
    if request.path.startswith("/items") or request.path.startswith("/health"):
        return jsonify({"error": "Not found"}), 404
    if os.path.isfile(os.path.join(public_dir, request.path.lstrip("/"))):
        return send_from_directory(public_dir, request.path.lstrip("/"))
    return send_from_directory(public_dir, "index.html")


if __name__ == "__main__":
    app.run(debug=False)

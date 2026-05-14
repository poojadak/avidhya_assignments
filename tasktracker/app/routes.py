from flask import Blueprint, request, jsonify, abort
from datetime import datetime, timezone
import uuid

from . import tasks

bp = Blueprint("tasks", __name__)


def make_task(title, description="", status="todo"):
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@bp.route("/tasks", methods=["GET"])
def list_tasks():
    status_filter = request.args.get("status")
    result = list(tasks.values())
    if status_filter:
        result = [t for t in result if t["status"] == status_filter]
    return jsonify(result)


@bp.route("/tasks", methods=["POST"])
def create_task():
    body = request.get_json(silent=True) or {}
    title = body.get("title", "").strip()
    if not title:
        abort(400, description="title is required")
    status = body.get("status", "todo")
    if status not in ("todo", "in_progress", "done"):
        abort(400, description="status must be todo, in_progress, or done")
    task = make_task(title, body.get("description", ""), status)
    tasks[task["id"]] = task
    return jsonify(task), 201


@bp.route("/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    task = tasks.get(task_id)
    if task is None:
        abort(404, description="task not found")
    return jsonify(task)


@bp.route("/tasks/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = tasks.get(task_id)
    if task is None:
        abort(404, description="task not found")
    body = request.get_json(silent=True) or {}
    if "title" in body:
        title = body["title"].strip()
        if not title:
            abort(400, description="title cannot be empty")
        task["title"] = title
    if "description" in body:
        task["description"] = body["description"]
    if "status" in body:
        if body["status"] not in ("todo", "in_progress", "done"):
            abort(400, description="status must be todo, in_progress, or done")
        task["status"] = body["status"]
    return jsonify(task)


@bp.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = tasks.pop(task_id, None)
    if task is None:
        abort(404, description="task not found")
    return "", 204

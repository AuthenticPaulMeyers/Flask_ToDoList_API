from flask import Blueprint

todos = Blueprint("todos", __name__, url_prefix="/todos")


@todos.post("/add")
def add_todo():
    return ({"message": "task added"})
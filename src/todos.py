from flask import Blueprint, request, jsonify
from src.constants.http_status_codes import  HTTP_200_OK, HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from src.database import db, Todo
from  flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

todos = Blueprint("todos", __name__, url_prefix="/todos")


@todos.post("/add")
@jwt_required()
def add_todo():
    current_user_id=get_jwt_identity()

    if request.method == "POST":
        title = request.get_json().get('title')
        description = request.get_json().get('description')
        
        # check for the existence of the title in the db
        if Todo.query.filter_by(title=title).first():
            return jsonify({"error": 'todo already exist'}), HTTP_409_CONFLICT
        # check if the title and description is not empty
        if title is " " or description is " ":
            return jsonify({"error": 'title or description cannot be null'})
        
        # add task to the database
        todo=Todo(title=title, description=description, user_id=current_user_id)
        db.session.add(todo)
        db.session.commit()

        return jsonify({
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'created_at': todo.create_at,
            'updated_at': todo.updated_at
        }), HTTP_201_CREATED

# get all todo
@todos.get('/all')
@jwt_required()
def all_todos():
    current_user_id=get_jwt_identity()
    # implement pagination
    page=request.args.get('page', 1, type=int)
    per_page=request.args.get('per_page', 6, type=int)

    #  using the GET request to retrieve todos
    todos=Todo.query.filter_by(user_id=current_user_id).order_by(Todo.create_at.desc()).paginate(page=page, per_page=per_page)
    data = []
        
    for todo in todos.items:
        data.append(
            {
                'id': todo.id,
                'title': todo.title,
                'description': todo.description,
                'created_at': todo.create_at,
                'updated_at': todo.updated_at
                }
            )
    metadata={
        'page': todos.page,
        'per_page':todos.per_page,
        'has_next': todos.has_next,
        'has_prev': todos.has_prev,
        'total': todos.total,
        'next_page': todos.next_num,
        'prev_page': todos.prev_num
    }
    return jsonify({'data': data, 'metadata': metadata}), HTTP_200_OK

# get a single todo
@todos.get('/<int:id>')
@jwt_required()
def get_todo(id):
    current_user_id=get_jwt_identity()

    #  using the GET request to retrieve todos
    todo=Todo.query.filter_by(id=id, user_id=current_user_id).first()
    if todo:
        return jsonify(
            {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'created_at': todo.create_at,
            'updated_at': todo.updated_at
            }
        ), HTTP_200_OK
    else:
        return jsonify({'error': f'{HTTP_404_NOT_FOUND} File not found'}), HTTP_404_NOT_FOUND

# delete task
@todos.delete('<int:id>')
@jwt_required()
def delete_todo(id):
    current_user_id=get_jwt_identity()

    todo=Todo.query.filter_by(id=id, user_id=current_user_id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        
        return jsonify({}), HTTP_204_NO_CONTENT
    else:
        return jsonify({'error': f'{HTTP_404_NOT_FOUND} File not found'}), HTTP_404_NOT_FOUND
        
# update route
@todos.put("/update/<int:id>")
@todos.patch("/update/<int:id>")
@jwt_required()
def update_todo(id):
    current_user_id=get_jwt_identity()

    
    todo=Todo.query.filter_by(id=id, user_id=current_user_id).first()
    
    if todo:
        title = request.get_json().get('title')
        description = request.get_json().get('description')

        if title is " " or description is " ":
            return jsonify({"error": 'title or description cannot be null'})
        
        todo.title = title
        todo.description = description

        return jsonify({
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'created_at': todo.create_at,
            'updated_at': todo.updated_at
        }), HTTP_201_CREATED
    else:
        return jsonify({'error': f'{HTTP_400_BAD_REQUEST,} Bad request'}), HTTP_400_BAD_REQUEST,






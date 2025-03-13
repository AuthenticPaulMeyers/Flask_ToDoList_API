from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# create tables
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(30), unique=True, nullable=False)
    email=db.Column(db.String(90), unique=True, nullable=False)
    password_hash=db.Column(db.Text, nullable=False)
    create_at=db.Column(db.DateTime, default=datetime.now())
    updated_at=db.Column(db.DateTime, onupdate=datetime.now())
    todos=db.Relationship('Todo', backref='user')
    def __repr__(self) -> str:
        return f'User>>> {self.name}'

class Todo(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(30), unique=True, nullable=False)
    description=db.Column(db.Text, unique=False, nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey("user.id"))
    create_at=db.Column(db.DateTime, default=datetime.now())
    updated_at=db.Column(db.DateTime, onupdate=datetime.now())
    def __repr__(self) -> int:
        return f'Todo>>> {self.id}'
    


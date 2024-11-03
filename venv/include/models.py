from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Поле для определения администратора
    info = db.Column(db.String(128), nullable=True, default='001')  # Новое поле для технической информации

    # Проверка пароля
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Модель книги
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    genre = db.Column(db.String(64))
    rating = db.Column(db.Float)
    chapters = db.relationship('Chapter', backref='book', lazy=True)

# Модель главы
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(128))
    content = db.Column(db.Text)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    

class Promt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(3), nullable=False, default='NEW')  # Новое поле status
    n_text = db.Column(db.String(4096), nullable=True)              # Новое поле n_text
    text = db.Column(db.String(4096), nullable=True)                # Изменённое поле text
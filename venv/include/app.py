import os
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Импортируем Migrate
from sqlalchemy.exc import IntegrityError
import jwt
import datetime
from models import db, User, Book, Chapter, Promt  
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Настройки приложения
app.config['SECRET_KEY'] = 'lolpi-top!net2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aibook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)

# Инициализация миграций
migrate = Migrate(app, db)  # Добавляем Migrate

# Функция для создания JWT
def create_jwt(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=48)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")

# Функция для проверки JWT
def verify_jwt(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None  # Токен истек
    except jwt.InvalidTokenError:
        return None  # Невалидный токен

# Маршрут для инициализации базы данных и добавления данных (однократно)
def create_tables():
    # Добавляем тестовых пользователей, если их нет
    if not User.query.filter_by(username='admin').first():
        try:
            user1 = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                info='101'
            )
            user2 = User(
                username='user',
                password_hash=generate_password_hash('password123'),
                info='001'
            )
            user3 = User(
                username='dasha',
                password_hash=generate_password_hash('dasha123'),
                info='001'
            )
            user4 = User(
                username='alia',
                password_hash=generate_password_hash('alia123'),
                info='001'
            )
            db.session.add_all([user1, user2, user3, user4])
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    # Добавляем несколько книг и глав, если их нет
    if not Book.query.first():
        book1 = Book(title='Название книги 1', description='Описание книги 1...', genre='Фантастика', rating=4.5)
        book2 = Book(title='Название книги 2', description='Описание книги 2...', genre='Роман', rating=4.0)
        book3 = Book(title='Название книги 3', description='Описание книги 3...', genre='Триллер', rating=4.8)
        db.session.add_all([book1, book2, book3])
        db.session.commit()

        # Добавляем главы для книг
        chapter1 = Chapter(number=1, title='Глава 1', content='Содержимое главы 1 книги 1...', book=book1)
        chapter2 = Chapter(number=2, title='Глава 2', content='Содержимое главы 2 книги 1...', book=book1)
        chapter3 = Chapter(number=1, title='Глава 1', content='Содержимое главы 1 книги 2...', book=book2)
        db.session.add_all([chapter1, chapter2, chapter3])
        db.session.commit()

# Главная страница
@app.route('/')
def index():
    token = request.cookies.get('token')
    if token:
        username = verify_jwt(token)
        if username:
            # Получаем список книг
            books = Book.query.all()
            return render_template('index.html', username=username, books=books)
        else:
            return "<h1>Токен не валиден или истек. <a href='/login'>Войти снова</a></h1>"
    else:
        return redirect(url_for('login'))
    
@app.route('/profile')
def profile():
    token = request.cookies.get('token')
    if token:
        username = verify_jwt(token)
        if username:
            # Получаем список книг
            books = Book.query.all()
            return render_template('profile.html', username=username, books=books)
        else:
            return "<h1>Токен не валиден или истек. <a href='/login'>Войти снова</a></h1>"
    else:
        return redirect(url_for('login'))

# Маршрут для отображения книги и глав
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    token = request.cookies.get('token')
    if token:
        username = verify_jwt(token)
        if username:
            book = db.session.get(Book, book_id)
            if not book:
                abort(404, description="Книга не найдена.")
            chapters = book.chapters
            return render_template('book_detail.html', book=book, chapters=chapters)
        else:
            return "<h1>Токен не валиден или истек. <a href='/login'>Войти снова</a></h1>"
    else:
        return redirect(url_for('login')) 

# Маршрут для отображения главы
@app.route('/book/<int:book_id>/chapter/<int:chapter_number>')
def chapter_detail(book_id, chapter_number):
    token = request.cookies.get('token')
    if token:
        username = verify_jwt(token)
        if username:
            chapter = Chapter.query.filter_by(book_id=book_id, number=chapter_number).first_or_404()
            return render_template('chapter_detail.html', chapter=chapter, username=username)
        else:
            return "<h1>Токен не валиден или истек. <a href='/login'>Войти снова</a></h1>"
    else:
        return redirect(url_for('login'))

# Маршрут для следующей главы
@app.route('/next_chapter', methods=['POST'])
def next_chapter():
    data = request.get_json()
    current_chapter_id = data.get('current_chapter_id')
    chapter = Chapter.query.get(current_chapter_id)
    if not chapter:
        return jsonify({'message': 'Глава не найдена.'}), 404
    next_chapter = Chapter.query.filter_by(book_id=chapter.book_id, number=chapter.number + 1).first()
    if next_chapter:
        response = {
            'chapter_id': next_chapter.id,
            'chapter_content': next_chapter.content
        }
    else:
        response = {'message': 'Это последняя глава.'}
    return jsonify(response)

# Маршрут для предыдущей главы
@app.route('/previous_chapter', methods=['POST'])
def previous_chapter():
    data = request.get_json()
    current_chapter_id = data.get('current_chapter_id')
    chapter = Chapter.query.get(current_chapter_id)
    if not chapter:
        return jsonify({'message': 'Глава не найдена.'}), 404
    prev_chapter = Chapter.query.filter_by(book_id=chapter.book_id, number=chapter.number - 1).first()
    if prev_chapter:
        response = {
            'chapter_id': prev_chapter.id,
            'chapter_content': prev_chapter.content
        }
    else:
        response = {'message': 'Это первая глава.'}
    return jsonify(response)

# Маршрут для сокращения текста
@app.route('/shorten_text', methods=['POST'])
def shorten_text():
    data = request.get_json()
    chapter_id = data.get('chapter_id')
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return jsonify({'message': 'Глава не найдена.'}), 404
    original_text = chapter.content
    shortened_text = ' '.join(original_text.split()[:50]) + '...'
    response = {'shortened_text': shortened_text}
    return jsonify(response)

# Маршрут для отображения сути
@app.route('/show_essence', methods=['POST'])
def show_essence():
    data = request.get_json()
    chapter_id = data.get('chapter_id')
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        return jsonify({'message': 'Глава не найдена.'}), 404
    original_text = chapter.content
    essence = ' '.join(original_text.split()[:20]) + '...'
    response = {'essence': essence}
    return jsonify(response)

# Тестовая функция
@app.route('/test_function')
def test_function():
    data = {'message': 'Тестовая функция выполнена успешно!'}
    return jsonify(data)

# Отправка баг-репорта
@app.route('/report_bug', methods=['POST'])
def report_bug():
    report = request.get_json()
    description = report.get('description')
    if not description:
        return jsonify({'message': 'Описание ошибки не предоставлено.'}), 400
    print(f'Получен баг-репорт: {description}')
    data = {'message': 'Спасибо за ваш отчет!'}
    return jsonify(data)

# Оценка книги
@app.route('/rate', methods=['POST'])
def rate():
    rating_data = request.get_json()
    rating = rating_data.get('rating')
    book_id = rating_data.get('book_id')
    
    if rating is None or book_id is None:
        return jsonify({'message': 'Неверные данные для оценки.'}), 400

    try:
        rating = float(rating)
        if not (1 <= rating <= 5):
            raise ValueError
    except ValueError:
        return jsonify({'message': 'Оценка должна быть числом от 1 до 5.'}), 400

    book = db.session.get(Book, book_id)
    if book:
        # Обновление рейтинга книги (простой пример усреднения)
        if book.rating:
            book.rating = (book.rating + rating) / 2
        else:
            book.rating = rating
        db.session.commit()
        data = {'message': 'Спасибо за вашу оценку!'}
    else:
        data = {'message': 'Книга не найдена.'}
    return jsonify(data)

# Маршрут для авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return "<h1>Пожалуйста, заполните все поля!</h1><a href='/login'>Попробовать снова</a>"

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            token = create_jwt(username)
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('token', token)
            return resp
        else:
            return "<h1>Неверный логин или пароль!</h1><a href='/login'>Попробовать снова</a>"

    return render_template('login.html')

# Маршрут для выхода
@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('token', '', expires=0)
    return resp

if __name__ == '__main__':
    # Создаём контекст приложения для выполнения миграций и инициализации данных
    with app.app_context():
        create_tables()  # Выполняем инициализацию перед запуском
    app.run(host='0.0.0.0', port=5000, debug=True)
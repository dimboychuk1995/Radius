# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import logging
from functools import wraps
from bson.objectid import ObjectId
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Настраиваем логирование
logging.basicConfig(level=logging.ERROR)

# Создаем Blueprint для аутентификации
auth_bp = Blueprint('auth', __name__)

# Настройки подключения к MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['trucks_db']
    users_collection = db['users']  # Коллекция для пользователей
    client.admin.command('ping')
    logging.info("Successfully connected to MongoDB")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    exit(1)

# Настраиваем Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Указываем функцию для отображения страницы логина
login_manager.login_message = "Пожалуйста, войдите для доступа к этой странице."  # Сообщение при попытке доступа к защищенной странице

# Класс User для Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password = user_data['password']
        self.role = user_data['role']

    @staticmethod
    def get(user_id):
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return None
        return User(user)


# Функция загрузки пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Функция для добавления пользователя
def add_user(username, password, role="user"):
    hashed_password = generate_password_hash(password)
    user = {'username': username, 'password': hashed_password, 'role': role}
    users_collection.insert_one(user)

# Создаем пользователей при первом запуске (если их еще нет)
if users_collection.find_one({'username': 'admin'}) is None:
    add_user('admin', 'password', 'admin')  # Пароль 'password'
if users_collection.find_one({'username': 'user'}) is None:
    add_user('user', 'password', 'user')  # Пароль 'password'

# Функция для проверки роли пользователя
def requires_role(role):
    def decorator(f):
        @wraps(f)
        @login_required  # Теперь используем декоратор Flask-Login
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                flash(f'Требуется роль {role}', 'danger')
                return redirect(url_for('trucks.trucks_list'))  # Изменено
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.before_app_request
def load_user():
    g.user = current_user if current_user.is_authenticated else None


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = users_collection.find_one({'username': username})

        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data)
            login_user(user)  # Используем функцию Flask-Login для логина
            flash('Успешный вход!', 'success')
            return redirect(request.args.get('next') or url_for('trucks.trucks_list'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()  # Используем функцию Flask-Login для логаута
    flash('Вы вышли из системы!', 'info')
    return redirect(url_for('auth.login'))

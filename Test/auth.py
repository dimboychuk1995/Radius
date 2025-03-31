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
login_manager.login_view = 'auth.login'
login_manager.login_message = "Пожалуйста, войдите для доступа к этой странице."

# Определяем допустимые роли
USER_ROLES = ['admin', 'user', 'dispatch']

# Класс User для Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password = user_data['password']
        self.role = user_data['role']
        self.company = user_data.get('company') # Изменено: получаем компанию

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
def add_user(username, password, role="user", company=None): # Изменено: добавлен параметр company
    hashed_password = generate_password_hash(password)
    user = {'username': username, 'password': hashed_password, 'role': role, 'company': company} # Изменено: сохраняем компанию
    users_collection.insert_one(user)

# Создаем пользователей при первом запуске (если их еще нет)
if users_collection.find_one({'username': 'admin'}) is None:
    add_user('admin', 'password', 'admin', 'UWC') # Изменено: добавлена компания
if users_collection.find_one({'username': 'user'}) is None:
    add_user('user', 'password', 'user', 'UWC') # Изменено: добавлена компания

# Функция для проверки роли пользователя
def requires_role(role):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                flash(f'Требуется роль {role}', 'danger')
                return redirect(url_for('trucks.trucks_list'))
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
            login_user(user)
            flash('Успешный вход!', 'success')
            return redirect(request.args.get('next') or url_for('trucks.trucks_list'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/users')
@login_required
@requires_role('admin')
def users_list():
    users = list(users_collection.find())
    for user in users:
        user['_id'] = str(user['_id'])
    return render_template('users.html', users=users, user_roles=USER_ROLES)

@auth_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@requires_role('admin')
def add_user_route():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        company = request.form.get('company') # Изменено: получаем компанию из формы
        if role not in USER_ROLES:
            flash('Недопустимая роль пользователя.', 'danger')
            return redirect(url_for('auth.users_list'))
        add_user(username, password, role, company) # Изменено: передаем компанию
        flash('Пользователь успешно добавлен.', 'success')
        return redirect(url_for('auth.users_list'))
    return render_template('add_user.html', user_roles=USER_ROLES)

@auth_bp.route('/users/delete/<user_id>', methods=['POST'])
@login_required
@requires_role('admin')
def delete_user(user_id):
    try:
        users_collection.delete_one({'_id': ObjectId(user_id)})
        flash('Пользователь успешно удален.', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении пользователя: {e}', 'danger')
    return redirect(url_for('auth.users_list'))
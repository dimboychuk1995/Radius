import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import traceback

from Test.auth import requires_role

# Настраиваем логирование
logging.basicConfig(level=logging.ERROR)

# Создаем Blueprint для функциональности грузовиков
trucks_bp = Blueprint('trucks', __name__)

# Настройки подключения к MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['trucks_db']
    trucks_collection = db['trucks']
    client.admin.command('ping')
    logging.info("Successfully connected to MongoDB")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    exit(1)

UPLOAD_FOLDER = 'uploads'  # Определите папку для загрузки файлов
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # Определите разрешенные расширения файлов


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@trucks_bp.route('/list', methods=['GET'])
@login_required
def trucks_list():
    try:
        trucks = list(trucks_collection.find())
        for truck in trucks:
            truck['_id'] = str(truck['_id'])
            if "file" not in truck:  # Добавлена проверка
                truck["file"] = None
        return render_template('trucks.html', trucks=trucks, username=current_user.username)
    except Exception as e:
        logging.error(f"Error fetching trucks: {e}")
        return render_template('error.html', message=f"Failed to retrieve truck list. Error: {e}")  # Изменено


@trucks_bp.route('/add_truck', methods=['POST'])
@requires_role('admin')
def add_truck():
    if request.method == 'POST':
        try:
            file_url = None
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
                    try:
                        file.save(file_path)
                        file_url = f'/{UPLOAD_FOLDER}/{filename}'
                    except Exception as e:
                        logging.error(f"Error saving file: {e}")
                        logging.error(traceback.format_exc())
                        return render_template("error.html", message=f"Ошибка сохранения файла. {e}")

            truck_data = {
                'year': request.form.get('year'),
                'make': request.form.get('make'),
                'model': request.form.get('model'),
                'mileage': request.form.get('mileage'),
                'vin': request.form.get('vin'),
                'file': file_url
            }
            trucks_collection.insert_one(truck_data)
            return redirect(url_for('trucks.trucks_list'))
        except Exception as e:
            logging.error(f"Error adding truck: {e}")
            logging.error(traceback.format_exc())
            return render_template('error.html', message="Failed to add truck")


@trucks_bp.route('/edit_truck/<truck_id>', methods=['POST'])
@requires_role('admin')
def edit_truck(truck_id):
    if request.method == 'POST':
        try:
            file_url = request.form.get('existing_file')  # Получаем url существующего файла
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
                    try:
                        file.save(file_path)
                        file_url = f'/{UPLOAD_FOLDER}/{filename}'
                    except Exception as e:
                        logging.error(f"Error saving file: {e}")
                        logging.error(traceback.format_exc())
                        return render_template("error.html", message=f"Ошибка сохранения файла. {e}")

            updated_data = {
                'year': request.form.get('year'),
                'make': request.form.get('make'),
                'model': request.form.get('model'),
                'mileage': request.form.get('mileage'),
                'vin': request.form.get('vin'),
                'file': file_url
            }
            trucks_collection.update_one({'_id': ObjectId(truck_id)}, {'$set': updated_data})
            return redirect(url_for('trucks.trucks_list'))
        except Exception as e:
            logging.error(f"Error updating truck: {e}")
            logging.error(traceback.format_exc())
            return render_template('error.html', message="Failed to edit truck")


@trucks_bp.route('/delete_truck/<truck_id>', methods=['POST'])
@requires_role('admin')
def delete_truck(truck_id):
    try:
        trucks_collection.delete_one({'_id': ObjectId(truck_id)})
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error deleting truck: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete truck'})
import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, send_file
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import traceback
from io import BytesIO

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

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
TRUCK_TYPES = ['Пикап', 'Семи']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@trucks_bp.route('/list', methods=['GET'])
@login_required
def trucks_list():
    try:
        # Изменено: фильтрация по компании
        trucks = list(trucks_collection.find({'company': current_user.company}))
        for truck in trucks:
            truck['_id'] = str(truck['_id'])
            if "file_data" not in truck:
                truck["file_data"] = None
                truck["file_name"] = None
                truck["file_mimetype"] = None
            if "unit_number" not in truck:
                truck["unit_number"] = None
            if "company" not in truck:
                truck["company"] = None
        return render_template('trucks.html', trucks=trucks, username=current_user.username, truck_types=TRUCK_TYPES)
    except Exception as e:
        logging.error(f"Error fetching trucks: {e}")
        return render_template('error.html', message=f"Failed to retrieve truck list. Error: {e}")


@trucks_bp.route('/add_truck', methods=['POST'])
@requires_role('admin')
def add_truck():
    if request.method == 'POST':
        try:
            file_data = None
            file_name = None
            file_mimetype = None
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    file_name = secure_filename(file.filename)
                    file_mimetype = file.mimetype
                    file_data = file.read()

            truck_data = {
                'year': request.form.get('year'),
                'make': request.form.get('make'),
                'model': request.form.get('model'),
                'mileage': request.form.get('mileage'),
                'vin': request.form.get('vin'),
                'file_data': file_data,
                'file_name': file_name,
                'file_mimetype': file_mimetype,
                'type': request.form.get('type'),
                'unit_number': request.form.get('unit_number'),
                'company': current_user.company
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
            file_data = None
            file_name = None
            file_mimetype = None
            if 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    file_name = secure_filename(file.filename)
                    file_mimetype = file.mimetype
                    file_data = file.read()

            updated_data = {
                'year': request.form.get('year'),
                'make': request.form.get('make'),
                'model': request.form.get('model'),
                'mileage': request.form.get('mileage'),
                'vin': request.form.get('vin'),
                'file_data': file_data,
                'file_name': file_name,
                'file_mimetype': file_mimetype,
                'type': request.form.get('type'),
                'unit_number': request.form.get('unit_number'),
                'company': current_user.company
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


@trucks_bp.route('/get_file/<truck_id>')
@login_required
def get_file(truck_id):
    try:
        truck = trucks_collection.find_one({'_id': ObjectId(truck_id)})
        if truck and truck['file_data']:
            return send_file(BytesIO(truck['file_data']),
                             download_name=truck['file_name'],
                             mimetype=truck['file_mimetype'],
                             as_attachment=True)
        else:
            return "File not found", 404
    except Exception as e:
        logging.error(f"Error getting file: {e}")
        return "Error getting file", 500
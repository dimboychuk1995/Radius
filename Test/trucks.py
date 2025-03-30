from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, g
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
from flask_login import login_required, current_user

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

@trucks_bp.route('/list', methods=['GET']) #Изменено
@login_required
def trucks_list():
    try:
        trucks = list(trucks_collection.find())
        for truck in trucks:
            truck['_id'] = str(truck['_id'])
        return render_template('trucks.html', trucks=trucks, username=current_user.username)
    except Exception as e:
        logging.error(f"Error fetching trucks: {e}")
        return render_template('error.html', message="Failed to retrieve truck list")

@trucks_bp.route('/add_truck', methods=['POST'])
@requires_role('admin')
def add_truck():
    if request.method == 'POST':
        try:
            truck_data = {
                'year': request.form.get('year'),
                'make': request.form.get('make'),
                'model': request.form.get('model'),
                'mileage': request.form.get('mileage'),
                'vin': request.form.get('vin')
            }
            trucks_collection.insert_one(truck_data)
            return redirect(url_for('trucks.trucks_list'))
        except Exception as e:
            logging.error(f"Error adding truck: {e}")
            return render_template('error.html', message="Failed to add truck")

@trucks_bp.route('/edit_truck/<truck_id>', methods=['POST'])
@requires_role('admin')
def edit_truck(truck_id):
    if request.method == 'POST':
        try:
            updated_data = {
                'year': request.form.get('year'),
                'make': request.form.get('make'),
                'model': request.form.get('model'),
                'mileage': request.form.get('mileage'),
                'vin': request.form.get('vin')
            }
            trucks_collection.update_one({'_id': ObjectId(truck_id)}, {'$set': updated_data})
            return redirect(url_for('trucks.trucks_list'))
        except Exception as e:
            logging.error(f"Error updating truck: {e}")
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
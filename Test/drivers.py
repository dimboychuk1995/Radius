from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
from flask_login import login_required, current_user

from Test.auth import requires_role

# Настраиваем логирование
logging.basicConfig(level=logging.ERROR)

# Создаем Blueprint для функциональности водителей
drivers_bp = Blueprint('drivers', __name__)

# Настройки подключения к MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['trucks_db']
    drivers_collection = db['drivers']
    client.admin.command('ping')
    logging.info("Successfully connected to MongoDB")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")
    exit(1)


@drivers_bp.route('/drivers', methods=['GET'])
@login_required
def drivers_list():
    try:
        # Изменено: фильтрация по компании
        drivers = list(drivers_collection.find({'company': current_user.company}))
        for driver in drivers:
            driver['_id'] = str(driver['_id'])
            if "company" not in driver:
                driver["company"] = None
        return render_template('drivers.html', drivers=drivers)
    except Exception as e:
        logging.error(f"Error fetching drivers: {e}")
        return render_template('error.html', message="Failed to retrieve drivers list")


@drivers_bp.route('/add_driver', methods=['POST'])
@requires_role('admin')
def add_driver():
    if request.method == 'POST':
        try:
            driver_data = {
                'name': request.form.get('name'),
                'license_number': request.form.get('license_number'),
                'contact_number': request.form.get('contact_number'),
                'company': current_user.company
            }
            drivers_collection.insert_one(driver_data)
            return redirect(url_for('drivers.drivers_list'))
        except Exception as e:
            logging.error(f"Error adding driver: {e}")
            return render_template('error.html', message="Failed to add driver")


@drivers_bp.route('/edit_driver/<driver_id>', methods=['POST'])
@requires_role('admin')
def edit_driver(driver_id):
    if request.method == 'POST':
        try:
            updated_data = {
                'name': request.form.get('name'),
                'license_number': request.form.get('license_number'),
                'contact_number': request.form.get('contact_number'),
                'company': current_user.company
            }
            drivers_collection.update_one({'_id': ObjectId(driver_id)}, {'$set': updated_data})
            return redirect(url_for('drivers.drivers_list'))
        except Exception as e:
            logging.error(f"Error updating driver: {e}")
            return render_template('error.html', message="Failed to edit driver")


@drivers_bp.route('/delete_driver/<driver_id>', methods=['POST'])
@requires_role('admin')
def delete_driver(driver_id):
    try:
        drivers_collection.delete_one({'_id': ObjectId(driver_id)})
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error deleting driver: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete driver'})
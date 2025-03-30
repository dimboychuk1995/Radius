from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Настройки подключения к MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Замените на ваши настройки
db = client['trucks_db']  # Название вашей базы данных
trucks_collection = db['trucks']  # Название коллекции с грузовиками


@app.route('/')
def trucks_list():
    trucks = list(trucks_collection.find())
    for truck in trucks:
        truck['_id'] = str(truck['_id'])
    return render_template('trucks.html', trucks=trucks)


@app.route('/add_truck', methods=['POST'])
def add_truck():
    if request.method == 'POST':
        truck_data = {
            'year': request.form.get('year'),
            'make': request.form.get('make'),
            'model': request.form.get('model'),
            'mileage': request.form.get('mileage'),
            'vin': request.form.get('vin')
        }
        trucks_collection.insert_one(truck_data)
        return redirect(url_for('trucks_list'))


@app.route('/edit_truck/<truck_id>', methods=['POST'])
def edit_truck(truck_id):
    if request.method == 'POST':
        updated_data = {
            'year': request.form.get('year'),
            'make': request.form.get('make'),
            'model': request.form.get('model'),
            'mileage': request.form.get('mileage'),
            'vin': request.form.get('vin')
        }
        trucks_collection.update_one({'_id': ObjectId(truck_id)}, {'$set': updated_data})
        return redirect(url_for('trucks_list'))


@app.route('/delete_truck/<truck_id>', methods=['POST'])
def delete_truck(truck_id):
    trucks_collection.delete_one({'_id': ObjectId(truck_id)})
    return jsonify({'success': True})  # Возвращаем JSON ответ
    # return redirect(url_for('trucks_list')) # Можно и так, но тогда js не нужен


if __name__ == '__main__':
    app.run(debug=True)

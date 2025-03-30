from flask import Flask, render_template, session, redirect, url_for
import logging
from auth import auth_bp, login_manager
from trucks import trucks_bp, trucks_list # Импортируем trucks_list
from drivers import drivers_bp
from flask_login import current_user

app = Flask(__name__)
app.secret_key = 'secret'

app.register_blueprint(auth_bp)
app.register_blueprint(trucks_bp)
app.register_blueprint(drivers_bp)
login_manager.init_app(app)

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Internal Server Error: {e}")
    return render_template('error.html', message="Internal Server Error"), 500

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('auth.login'))

@app.route('/trucks')
def trucks():
    return trucks_list() # Используем trucks_list из trucks.py

if __name__ == '__main__':
    app.run(debug=True)
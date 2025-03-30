# main.py
from flask import Flask, render_template, session, redirect, url_for
import logging
from auth import auth_bp, login_manager  # Import login_manager
from trucks import trucks_bp # Import trucks_bp

app = Flask(__name__)
app.secret_key = 'secret'  # Change to a secure random key

# Регистрируем Blueprint'ы
app.register_blueprint(auth_bp)
app.register_blueprint(trucks_bp)
login_manager.init_app(app)  # Initialize Flask-Login



# Глобальная обработка ошибок
@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Internal Server Error: {e}")
    return render_template('error.html', message="Internal Server Error"), 500

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('trucks.trucks_list'))
    else:
        return redirect(url_for('auth.login'))



if __name__ == '__main__':
    app.run(debug=True)
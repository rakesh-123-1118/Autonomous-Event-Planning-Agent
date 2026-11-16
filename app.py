import os
from flask import Flask, render_template

from config import APP_NAME, DATABASE_PATH, DEBUG, PORT, SECRET_KEY
from database.database import db
from routes.event_routes import bp as events_bp
from routes.task_routes import bp as tasks_bp
from routes.dashboard_routes import bp as dashboard_bp
from routes.chat_routes import bp as chat_bp


def create_app():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{DATABASE_PATH}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(events_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chat_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/create-event')
    def create_event_page():
        return render_template('create_event.html')

    @app.route('/planning')
    def planning_page():
        return render_template('planning.html')

    @app.route('/tasks')
    def tasks_page():
        return render_template('tasks.html')

    @app.route('/dashboard')
    def dashboard_page():
        return render_template('dashboard.html')

    @app.route('/recommendations')
    def recommendations_page():
        return render_template('recommendations.html')

    @app.route('/chat')
    def chat_page():
        return render_template('chat.html')

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT, host='0.0.0.0')

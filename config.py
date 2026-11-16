import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'app.db')

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{DATABASE_PATH}')
SQLALCHEMY_TRACK_MODIFICATIONS = False

APP_NAME = 'Autonomous Event Planning Agent'
DEBUG = os.getenv('DEBUG', 'True').lower() in ('1', 'true', 'yes')
PORT = int(os.getenv('PORT', '5000'))

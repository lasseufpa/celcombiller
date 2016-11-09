import flask
from flask_sqlalchemy import SQLAlchemy
import flask_restless
from flask_login import LoginManager
from flask_cors import CORS

from .config import PATH_TO_DATABASE, SECRET_KEY, DEBUG
# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = DEBUG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../' + PATH_TO_DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True




# Ability cross domain
cors = CORS(app)

db = SQLAlchemy(app)

app.secret_key = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)

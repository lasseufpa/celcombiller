from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import flask.ext.restless
from flask.ext.login import LoginManager
from flask.ext.cors import CORS
from config import path_to_database, secret_key

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path_to_database


# Ability cross domain
cors = CORS(app)

db = SQLAlchemy(app)

app.secret_key = secret_key
login_manager = LoginManager()
login_manager.init_app(app)

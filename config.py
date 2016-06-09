import flask
import flask.ext.sqlalchemy
import flask.ext.restless
from flask.ext.login import LoginManager
from flask.ext.cors import CORS

# adm login and password
adm_user = 'admin'
adm_pssw = 'adm123'


# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/vitor/celcombiller/alph.db'


# Ability cross domain
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

db = flask.ext.sqlalchemy.SQLAlchemy(app)

app.secret_key = 'abrakadabra'
login_manager = LoginManager()
login_manager.init_app(app)

import flask
import flask.ext.sqlalchemy
import flask.ext.restless
from flask.ext.login import LoginManager

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

db = flask.ext.sqlalchemy.SQLAlchemy(app)

app.secret_key = 'abrakadabra'
login_manager = LoginManager()
login_manager.init_app(app)
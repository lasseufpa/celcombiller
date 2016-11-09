from flask_jwt import JWT, jwt_required, current_identity

from src import routes
from src.setup import app
from src.config import DEBUG, PORT_TO_RUN
from src.schedule_system import start_schedule
from src.routes import authenticate,identity
start_schedule()

jwt = JWT(app, authenticate, identity)
# start the flask loop
app.debug = DEBUG
app.run('0.0.0.0', PORT_TO_RUN)

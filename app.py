import routes
from setup import app
from config import debug, port_to_run
from schedule_system import start_schedule

start_schedule()

# start the flask loop
app.debug = debug
app.run('0.0.0.0', port_to_run)

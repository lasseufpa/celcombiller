import routes
from setup import app
from schedule_system import start_schedule

start_schedule()

# start the flask loop
app.debug = True
app.run('0.0.0.0', 5000)

import routes
from setup import app

# start the flask loop
app.debug = True
app.run('0.0.0.0', 5000)

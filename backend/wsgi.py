from src import routes
from src.setup import app
from config import DEBUG, PORT_TO_RUN
from src.schedule_system import start_schedule



if __name__ == "__main__":
	start_schedule()
	
	# start the flask loop
	app.run()

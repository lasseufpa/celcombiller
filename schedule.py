from models import User, Schedules, ScheduleUser, VoiceBalance, DataBalance, ScheduleInput
from datetime import datetime, timedelta
from config import db

# check the last time schedule worked


def check_last():
    last_voice = VoiceBalance.query.filter_by(origin=u"schedule").order_by(
        VoiceBalance.date.desc()).first().date
    last_data = DataBalance.query.filter_by(origin=u"schedule").order_by(
        DataBalance.date.desc()).first().date
    return max(last_voice, last_data)


def run_schedule(day):
	#first we get the schedules of the day
	
	list_schedule = Schedules.query.filter_by(Schedules.day = day).all() 

	if not list_schedule:
		for schedule in list_schedule:
			#then we get the users of that schedule
			user_list = ScheduleUser.query.filter_by(ScheduleUser.schedule_id = schedule._id).all()
			if not user_list:
				for user in user_list:
					



# I'am there is a better way to do it, but...
# Why the f** are we doing it in this way ?
# Because if the difference between the date of last entry and the date 
# now is more tha one month we need to run some schedules more than one time 
# and I could not thing in other simple way of doing it   
def travel_schedules(last):
	diff = datetime.now() - last

	run_schedules(last.day)
	for i in xrange(diff.days):
		last += timedelta(1)
	 	run_schedule(last.day)


def schedule_routine(last=None):
	# check if we have the last check salved
	if not last:
    last = check_last()

    if (last.day != datetime.now().day) or
        (last.month != datetime.now().month):
        travel_schedules(last)
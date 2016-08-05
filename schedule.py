from models import User, Schedules, ScheduleUser, VoiceBalance, DataBalance, ScheduleInput
from datetime import datetime, timedelta
from setup import db
import schedule
import time

# most of the work here could have been done by trigger in the db but to keep the code
# portable I'm doing it through the ORM


def run_schedule(day):
    # first we get the schedules of the day
    list_schedule = Schedules.query.filter_by(Schedules.day=day).all()

    if not list_schedule:
        for schedule in list_schedule:
            # then we get the users of that schedule
            user_list = ScheduleUser.query.filter_by(ScheduleUser.schedule_id=schedule._id).all()
            if not user_list:
                for user in user_list:
                    # And then we add credit to the user and subtract one from the field count
                    # the field count if equal or less than 0 que remove the line from the db
                    if user.count > 1:
                        schedule_input = ScheduleInput(schedule._id, user.user.user_id)
                        db.session.add(schedule_input)
                        db.session.commit()
                        user.count -= 1

                    elif user.count == 1:
                        schedule_input = ScheduleInput(schedule._id, user.user.user_id)
                        ScheduleUser.query.filter_by(
                            user_id=user.user_id, schedule_id=schedule._id).delete()
                        db.session.add(schedule_input)
                        db.session.commit()

                    else:
                        ScheduleUser.query.filter_by(
                            user_id=user.user_id, schedule_id=schedule._id).delete()
                        db.session.commit()

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

# check the last time schedule worked


def check_last():
    last_voice = VoiceBalance.query.filter_by(origin=u"schedule").order_by(
        VoiceBalance.date.desc()).first().date
    last_data = DataBalance.query.filter_by(origin=u"schedule").order_by(
        DataBalance.date.desc()).first().date
    return max(last_voice, last_data)


def schedule_routine(last=None):
    # check if we have the last check salved
    if not last:
    last = check_last()

    if (last.day != datetime.now().day) or
        (last.month != datetime.now().month):
        travel_schedules(last)


def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)

def start_schedule(time):
    schedule.every().day.at(time).do(run_schedule)
    t = Thread(target=run_schedule)
    t.start()

from models import Schedules, ScheduleUser,\
    VoiceBalance, DataBalance, ScheduleInput
from datetime import datetime, timedelta
from setup import db
from config import schedule_verification_time
import schedule
import time
from threading import Thread

# most of the work here could have been done by trigger in the db but to keep
# the code portable I'm doing it through the ORM

firs_datetime = datetime(2016, 7, 2)


def credit_by_schedule(day):
    # first we get the schedules of the day
    list_schedule = Schedules.query.filter_by(day=day).all()

    if list_schedule:
        for schedule_object in list_schedule:
            # then we get the users of that schedule
            user_list = ScheduleUser.query.\
                filter_by(schedule_id=schedule_object._id).all()
            if user_list:
                for user in user_list:
                    # And then we add credit to the user and subtract one from
                    # the field count the field count if equal or less than 0
                    # remove the line from the db
                    if user.count > 1:
                        user.count -= 1
                        schedule_input = ScheduleInput(
                            schedule_object._id, user.user_id)
                        db.session.add(schedule_input)
                        db.session.commit()

                    elif user.count == 1:
                        schedule_input = ScheduleInput(
                            schedule_object._id, user.user_id)
                        ScheduleUser.query.filter_by(
                            user_id=user.user_id,
                            schedule_id=schedule_object._id
                        ).delete()
                        db.session.add(schedule_input)
                        db.session.commit()

                    else:
                        ScheduleUser.query.filter_by(
                            user_id=user.user_id,
                            schedule_id=schedule_object._id
                        ).delete()
                        db.session.commit()

# I'am there is a better way to do it, but...
# Why the f** are we doing it in this way ?
# Because if the difference between the date of last entry and the date
# now is more tha one month we need to run some schedules more than one time
# and I could not thing in other simple way of doing it


def travel_schedules(last):
    diff = datetime.now() - last

    credit_by_schedule(last.day)
    for i in xrange(diff.days):
        last += timedelta(1)
        credit_by_schedule(last.day)

# check the last time schedule worked


def check_last():
    last_voice = VoiceBalance.query.filter_by(origin=u"schedule").order_by(
        VoiceBalance.date.desc()).first()

    # if the last voice is empty
    if last_voice:
        last_voice = last_voice.date
    else:
        last_voice = firs_datetime

    last_data = DataBalance.query.filter_by(origin=u"schedule").order_by(
        DataBalance.date.desc()).first()

    # if the last data is empty
    if last_data:
        last_data = last_data.date
    else:
        last_data = firs_datetime

    return max(last_voice, last_data)


def schedule_routine(last=None):
    # check if we have the last check salved
    if not last:
        last = check_last()

    if (last.day != datetime.now().day) or\
            (last.month != datetime.now().month):
        travel_schedules(last)


def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


def start_schedule():
    schedule.every().day.at(schedule_verification_time).do(schedule_routine)
    t = Thread(target=run_schedule)
    t.daemon = True
    t.start()

from my_website import app,db
from my_website.customer import views
from my_website.admin import views
from flask_apscheduler import APScheduler

#Importing data_base.py to declare all ORM classes.
import data_base

#Creating all tables using create all inside structure_db funtion.
data_base.structure_db()

#initialize the apscheduler
sched = APScheduler()

#the cron job each day
def job1():
    from service import Schedule
    Schedule.send_mail()
    

if __name__ == "__main__":
    app.logger.debug("Running app now on port no 5000.")
    try:
        sched.add_job(id='job1',func=job1,trigger='cron',hour=6,minute = 5)
        sched.start()
    except Exception as e:
        app.logger.error("Unable to execute cronjob.")
    app.run(debug=False)
from my_website import app,db
from my_website.customer import views
from my_website.admin import views

#Importing data_base.py to declare all ORM classes.
import data_base

#Creating all tables using create all inside structure_db funtion.
data_base.structure_db()

if __name__ == "__main__":
    app.logger.debug("Running app now on port no 5000.")
    app.run(debug=False)
try:
    from flask_bcrypt import Bcrypt
    from flask_sqlalchemy import SQLAlchemy
    from flask import Flask
    import os
    import logging
except Exception as e:
    print("Could not import module in my_website package")

#get the root logger
logger = logging.getLogger()

#create a formatter object
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s : %(message)s')

# add console handler to the root logger
consoleHanlder = logging.StreamHandler()
consoleHanlder.setFormatter(log_formatter)
logger.addHandler(consoleHanlder)
logger.setLevel(logging.INFO)

#add file handler to the root logger
fileHandler = logging.FileHandler("logs.log")
fileHandler.setFormatter(log_formatter)
logger.addHandler(fileHandler)
logger.setLevel(logging.DEBUG)

# creating object of Flask class named app then setting SECRET_KEY
app = Flask(__name__)

# write first log in record.log
app.logger.debug("App object created of flask class.")

#setting up app config for SQLAlchemy 
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
db = SQLAlchemy(app)
app.logger.info("Object created of SQLAlchemy class.")

#binding Bcrypt to mathing plain text to hash value
bcrypt = Bcrypt(app)

# #config app for email server
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT']   = 465
# app.config['MAIL_USERNAME'] = os.environ.get('COMPANY_EMAIL')
# app.config['MAIL_PASSWORD'] = ''
# app.config['MAIL_USE_TLS']  = False
# app.config['MAIL_USE_SSL']  = True

















from flask import Flask
from logging.config import dictConfig
import logging


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
app.config["SECRET_KEY"] = "mysecretkey"

# write first log in record.log
app.logger.debug(" app object created of flask class")















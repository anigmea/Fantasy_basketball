from flask import Flask # import flask package
from config import Config # import Config class from config.py
from flask_moment import Moment # for date and time rendering (we need to convert times accurately for users in different areas)

app = Flask(__name__) # creates app VARIABLE as instance of class Flask (__name__ references the name of the module in which it is used (returns __main__?))
app.config.from_object(Config) # access sensitive info using something like app.config['<variable_name>']
db = 'TBA' # create a variable to reference our firebase database, with the url coming from app.config
moment = Moment(app) # for date and time rendering (we need to convert times accurately for users in different areas) (add {{ moment.include_moment() }} to base.html at bottom of <body></body> element)

from app import routes, errors # VERY IMPORTANT 









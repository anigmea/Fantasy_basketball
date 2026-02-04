from flask import Flask # import flask package
from config import Config # import Config class from config.py
from flask_moment import Moment # for date and time rendering (we need to convert times accurately for users in different areas)
import firebase_admin
from flask_cors import CORS
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5174"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
# creates app VARIABLE as instance of class Flask (__name__ references the name of the module in which it is used (returns __main__?))
app.config.from_object(Config) # access sensitive info using something like app.config['<variable_name>']

# firebase setup
cred = credentials.Certificate(app.config["FIREBASE_CREDENTIALS"])
firebase_admin.initialize_app(cred)
db = firestore.client() # create a variable to reference our firebase database, with the url coming from app.config

def save_analysis(user_id, analysis):
    db.collection("users").document(user_id).collection("analysis").add(analysis)

moment = Moment(app) # for date and time rendering (we need to convert times accurately for users in different areas) (add {{ moment.include_moment() }} to base.html at bottom of <body></body> element)

from app import routes, errors # VERY IMPORTANT 








import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__)) # get name of the directory holding __file__ (fantasy) and then get the absolute path leading to the directory
load_dotenv(os.path.join(basedir, '.env')) 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'TBA'
    FIREBASE_CREDENTIALS = os.environ.get("FIREBASE_CREDENTIALS") or 'TBA'
    SWID = os.environ.get("SWID") or 'TBA'
    ESPN_S2 = os.environ.get("ESPN_S2") or 'TBA'
    LEAGUE_ID = os.environ.get("LEAGUE_ID") or 'TBA'


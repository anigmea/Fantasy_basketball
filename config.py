import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__)) # get name of the directory holding __file__ (fantasy) and then get the absolute path leading to the directory
load_dotenv(os.path.join(basedir, '.env')) 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'TBA'
    DATABASE_URI = os.environ.get('DATABASE_URL', '') or 'TBA'
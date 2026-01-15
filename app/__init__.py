from flask import Flask # import flask package
app = Flask(__name__) # creates app VARIABLE as instance of class Flask (__name__ references the name of the module in which it is used (returns __main__?))
from app import routes # uses the app PACKAGE (directory, NOT THE VARIABLE DEFINED ABOVE) to import the routes module/file 













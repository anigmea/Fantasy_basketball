from app import app # import the app VARIABLE from the app MODULE/FILE
from app.forms import SearchForm
from app import db
from flask import flash, redirect, url_for # Important for user navigation
from flask import render_template # import the render_template() function to use the template from the index.html file in the templates folder
from flask import request # Flask provides a request variable that contains all the information that the client sent with the request (send user to the page they originally requested after they log in)
from urllib.parse import urlsplit # A function that parses a URL and has a .netloc component that reveals if the url is a relative path within the app or includes an outside domain name, which is dangerous and should be ignored


# ROUTE FOR PLAYER RANKINGS
@app.route('/', methods=['GET', 'POST']) # these decorators make the function below a "view function."
@app.route('/index', methods=['GET', 'POST']) # When a browser requests either of these 2 URLs Flask will return the result of this function as a response (just a print statement)
def index(): # this is a view function mapped to one or more route URLs so Flask knows what logic to execute when a client requests a given URL
    form = SearchForm()
    if form.validate_on_submit(): 
        # call database for user search here
        return redirect(url_for('index')) # refresh application to show changes (we ain't using websockets) (this will also have to take parameter)
    
    # Example Firestore query
    # results = (
    #     db.collection("users")
    #         .where("username", "==", query)
    #         .stream()
    #     )
    # users = [doc.to_dict() for doc in results]

    # Get players

    results = (
        db.collection("Players").stream()
    )
    players = [doc.to_dict() for doc in results] # [{'name': 'LeBron James'}, {'name': 'Michael Jordan'}]

    return render_template('index.html', title='TBA', form=form, players=players) # Not sure what deliverable the main page should present so title is 'TBA' for now

# ROUTE FOR PLAYER WAIVER/INJURY REPLACEMENT
@app.route('/replacements', methods=['GET', 'POST'])
def replacements():
    form = SearchForm()
    if form.validate_on_submit(): 
        # call database for user search here
        return redirect(url_for('replacements')) 

    # results = (
    #     db.collection("Players").stream()
    # )
    # players = [doc.to_dict() for doc in results] 
    replacements = []

    return render_template('replacements.html', title='TBA', form=form, replacements=replacements) # Not sure what deliverable the main page should present so title is 'TBA' for now

# ROUTE FOR Boom/bust
@app.route('/boombust', methods=['GET', 'POST'])
def boombust():
    form = SearchForm()
    if form.validate_on_submit(): 
        # call database for user search here
        return redirect(url_for('boombust')) 

    # results = (
    #     db.collection("Players").stream()
    # )
    # players = [doc.to_dict() for doc in results] 
    players = []

    return render_template('boombust.html', title='TBA', form=form, players=players) # Not sure what deliverable the main page should present so title is 'TBA' for now

# ROUTE FOR schedule tracker
@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    form = SearchForm()
    if form.validate_on_submit(): 
        # call database for user search here
        return redirect(url_for('schedule')) 

    # results = (
    #     db.collection("Players").stream()
    # )
    # players = [doc.to_dict() for doc in results] 
    teams = []

    return render_template('schedule.html', title='TBA', form=form, teams=teams) # Not sure what deliverable the main page should present so title is 'TBA' for now

# ROUTE FOR trade analyzer
@app.route('/trade', methods=['GET', 'POST'])
def trade():
    form = SearchForm()
    if form.validate_on_submit(): 
        # call database for user search here
        return redirect(url_for('trade')) 

    # results = (
    #     db.collection("Players").stream()
    # )
    # players = [doc.to_dict() for doc in results] 
    players = []

    return render_template('trade.html', title='TBA', form=form, players=players) # Not sure what deliverable the main page should present so title is 'TBA' for now
























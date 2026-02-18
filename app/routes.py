from app import app # import the app VARIABLE from the app MODULE/FILE
from app.forms import SearchForm
from app import db
from flask import flash, redirect, url_for # Important for user navigation
from flask import render_template # import the render_template() function to use the template from the index.html file in the templates folder
from flask import request # Flask provides a request variable that contains all the information that the client sent with the request (send user to the page they originally requested after they log in)
from urllib.parse import urlsplit # A function that parses a URL and has a .netloc component that reveals if the url is a relative path within the app or includes an outside domain name, which is dangerous and should be ignored
from app.espn_calls.boom_bust_calls import get_boom_bust_players
from app.models.waiver_regression import load_training_data, train_model


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

    # Get team players
    team_players = (
        db.collection("team_players").limit(10).stream() # only get 10 to avoid high reads during development
    )

    # Get free agents
    free_agents = (
        db.collection("free_agents").limit(10).stream() 
    )

    team_players = [doc.to_dict() for doc in team_players] # [{'name': 'LeBron James'}, {'name': 'Michael Jordan'}]
    free_agents = [doc.to_dict() for doc in free_agents]

    return render_template('index.html', title='Player Rankings', form=form, team_players=team_players, free_agents=free_agents)

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

    return render_template('replacements.html', title='Replacements', form=form, replacements=replacements) 

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

    return render_template('boombust.html', title='Boom/Bust', form=form, players=players)

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

    return render_template('schedule.html', title='Schedule', form=form, teams=teams)

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

    return render_template('trade.html', title='Trades', form=form, players=players)
























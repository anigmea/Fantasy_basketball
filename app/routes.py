from app import app # import the app VARIABLE from the app MODULE/FILE










@app.route('/') # these decorators make the function below a "view function."
@app.route('/index') # When a browser requests either of these 2 URLs Flask will return the result of this function as a response (just a print statement)
def index(): # this is a view function mapped to one or more route URLs so Flask knows what logic to execute when a client requests a given URL
    return "Hello, World!"
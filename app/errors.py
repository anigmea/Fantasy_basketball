from flask import render_template
from app import app, db

@app.errorhandler(404) # To declare a custom error handler, the @errorhandler decorator is used
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500) # database errors
def internal_error(error):
    # issue a command here to abort the session and remove any database changes made during it
    return render_template('500.html'), 500
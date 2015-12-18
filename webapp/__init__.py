# Import flask and template operators
from flask import Flask, render_template

# Define the WSGI application object
app = Flask(__name__, instance_relative_config=True)

# Configurations
app.config.from_object('config')
app.config.from_pyfile('config.py')

# Define the database object which is imported
# by modules and controllers
from database import db_session, init_db

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Import a module / component using its blueprint handler variable (mod_auth)
from webapp.mod_auth.controllers import mod_auth as auth_module
from webapp.controllers import invoicing

# Register blueprint(s)
app.register_blueprint(auth_module)
app.register_blueprint(invoicing)
# app.register_blueprint(xyz_module)
# ..

# Build the database:
# This will create the database file using SQLAlchemy
init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
	db_session.remove()
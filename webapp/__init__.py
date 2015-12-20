# Import flask and template operators
from flask import Flask, render_template
from flask.ext.login import LoginManager
import logging
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the WSGI application object
app = Flask(__name__, instance_relative_config=True)

# Configurations
app.config.from_object('config')
app.config.from_pyfile('config.py')

manager = Manager(app)
manager.add_command('db', MigrateCommand)

from database import engine, init_db, db_session, Base

migrate = Migrate(app, Base)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.signin'

from mod_auth.models import User, LoginUser

@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    session_user = LoginUser(user.name, user.id, user.status == 'active')
    return session_user

# Build the database:
# This will create the database file using SQLAlchemy
init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

def date_format(s):
    if s is not None:
        return s.strftime(app.config['DATE_FORMAT'])
    else:
        return "-"

app.jinja_env.filters['date_format'] = date_format

# Import a module / component using its blueprint handler variable (mod_auth)
from webapp.controllers import base
from webapp.mod_auth.controllers import mod_auth as auth_module
from webapp.invoicing.controllers import invoicing

# Register blueprint(s)
app.register_blueprint(base)
app.register_blueprint(auth_module)
app.register_blueprint(invoicing)
# app.register_blueprint(xyz_module)
# ..

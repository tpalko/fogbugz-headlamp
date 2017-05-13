# Import flask and template operators
import os
from flask import request, Flask, flash, render_template, g
from flask.ext.login import LoginManager
from flask.ext.migrate import Migrate
from flask.ext.babel import Babel, format_datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the WSGI application object
app = Flask(__name__, instance_relative_config=True)

# Configurations
app.config.from_object('config_default')
app.config.from_pyfile('config_%s.py' % os.environ['HEADLMP_ENVIRONMENT'])

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)

from models import Base
from invoicing.models import *

def init_db():
    Base.metadata.create_all(bind=engine)

def connect_db():
    return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))    

migrate = Migrate(app, Base)

babel = Babel(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.url_value_preprocessor
def set_print_mode(endpoint, values):
    g.print_view = request.args.get('print', False)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.signin'

from mod_auth.models import User, LoginUser

@login_manager.user_loader
def load_user(user_id):
    user = g.db.query(User).filter_by(id=user_id).first()
    session_user = None
    if user:
        session_user = LoginUser(user.name, user.id, user.is_active)

    g.user = session_user
    return session_user

# Build the database:
# This will create the database file using SQLAlchemy
init_db()

def date_format(s):
    if s is not None:
        return format_datetime(s, app.config['BABEL_DATE_FORMAT'])
    else:
        return "-"

def datetime_format(s):
    if s is not None:
        return format_datetime(s, format='long') #app.config['DATETIME_FORMAT'])#.lstrip("0").replace(" 0", " ")
    else:
        return "-"

def ticket(cases):
    return [ c.ticket_url() for c in cases ]

app.jinja_env.filters['date_format'] = date_format
app.jinja_env.filters['datetime_format'] = datetime_format
app.jinja_env.filters['ticket'] = ticket

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


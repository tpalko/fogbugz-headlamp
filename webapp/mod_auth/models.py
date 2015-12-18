# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from webapp.models import CustomBase
from sqlalchemy import Column, func, String, SmallInteger, Integer, DateTime

# Define a User model
class User(CustomBase):

    __tablename__ = 'auth_user'

    # User Name
    name    = Column(String(128),  nullable=False)

    # Identification Data: email & password
    email    = Column(String(128),  nullable=False,
                                            unique=True)
    password = Column(String(192),  nullable=False)

    # Authorisation Data: role & status
    role     = Column(SmallInteger, nullable=False)
    status   = Column(SmallInteger, nullable=False)

    # New instance instantiation procedure
    def __init__(self, name, email, password):

        self.name     = name
        self.email    = email
        self.password = password

        self.role = 'admin'
        self.status = 'active'

    def __repr__(self):
        return '<User %r>' % (self.name)    
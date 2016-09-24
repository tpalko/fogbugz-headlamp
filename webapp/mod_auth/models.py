from webapp.models import CustomBase
from sqlalchemy import Column, func, String, SmallInteger, Integer, DateTime, Boolean
from flask.ext.login import UserMixin

class LoginUser(UserMixin):
    
    is_anonymous = True
    is_authenticated = False
    is_active = False

    def __init__(self, name, id, active):
        self.name = name
        self.id = id
        self.is_active = active

    def is_active(self):
        return self.is_active

    def is_anonymous(self):
        return self.is_anonymous

    def is_authenticated(self):
        return self.is_authenticated

    def get_id(self):
        return unicode(self.id)

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
    role     = Column(String(32), nullable=False)
    is_active   = Column(Boolean, nullable=False)
    
    # New instance instantiation procedure
    def __init__(self, name, email, password):

        self.name     = name
        self.email    = email
        self.password = password

        self.role = 'admin'
        self.is_active = True

    def __repr__(self):
        return '<User %r>' % (self.name)    
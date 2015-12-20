from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

database_uri = 'sqlite:///webapp/webapp.db'

engine = create_engine(database_uri, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))    
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    from mod_auth import models
    from invoicing import models
    Base.metadata.create_all(bind=engine)  

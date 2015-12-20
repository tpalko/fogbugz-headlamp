from database import Base
from sqlalchemy import Column, func, String, SmallInteger, Integer, DateTime

# Define a base model for other database tables to inherit
class CustomBase(Base):

    __abstract__  = True

    id            = Column(Integer, primary_key=True)
    date_created  = Column(DateTime,  default=func.current_timestamp())
    date_modified = Column(DateTime,  default=func.current_timestamp(),
                                           onupdate=func.current_timestamp())

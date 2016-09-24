from sqlalchemy import Column, func, String, Text, SmallInteger, Integer, DateTime, NVARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper, ColumnProperty

Base = declarative_base()

# Define a base model for other database tables to inherit
class CustomBase(Base):

	__abstract__  = True

	id            = Column(Integer, primary_key=True)
	date_created  = Column(DateTime,  default=func.current_timestamp())
	date_modified = Column(DateTime,  default=func.current_timestamp(),
	                                       onupdate=func.current_timestamp())

	def columns(self):
	    """Return the actual columns of a SQLAlchemy-mapped object"""
	    return [prop.key for prop in class_mapper(self.__class__).iterate_properties if isinstance(prop, ColumnProperty) and prop.key not in ['id', 'date_created', 'date_modified']]

	def update(self, *args, **kwargs):
		for k in kwargs.keys():
			setattr(self, k, kwargs[k])
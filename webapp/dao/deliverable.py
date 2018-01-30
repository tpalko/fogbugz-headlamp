from flask import g
from webapp.invoicing.models import Deliverable

class DeliverableDAO:
	
	@staticmethod
	def all():
		return g.db.query(Deliverable).all()
from flask import g
from webapp.invoicing.models import Project

class ProjectDAO:
	
	@staticmethod
	def get(ixproject):
		return g.db.query(Project).filter(Project.ixproject==int(ixproject)).first()
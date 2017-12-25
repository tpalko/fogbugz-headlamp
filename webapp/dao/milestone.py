from flask import g
from webapp.invoicing.models import Milestone

class MilestoneDAO:

	@staticmethod
	def GetInvoiceMilestones(invoice_id):
		return g.db.query(Milestone).filter(Milestone.invoice_id==invoice_id).order_by(Milestone.ixproject, Milestone.dt)

	@staticmethod
	def GetCurrentInvoiceMilestones():
		return g.db.query(Milestone).filter(Milestone.bfrozen==True, Milestone.invoice==None).order_by(Milestone.ixproject, Milestone.dt)
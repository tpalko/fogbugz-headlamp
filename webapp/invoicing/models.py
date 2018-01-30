from sqlalchemy import Column, func, String, SmallInteger, Integer, DateTime, Boolean, Float, Date
from sqlalchemy.schema import Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from webapp import app
from webapp.models import CustomBase
from flask import g

'''
	FogbugzUserCase.cost()
		-> Case.cost()
			-> Milestone.cost() : Case.cost() for all cases
			-> Milestone.billable_cost() : Case.cost() for all non-comped, non-deliverable cases
				-> Invoice.billable_cost()
			-> Category.cost()
			-> Deliverable.balance() : estimate minus refunded amount and non-comped cases
			-> Deliverable.cost_in_milestone() : Case.cost() for all cases if case in given milestone

	Milestone.billable_cost() -> Milestone.finvoicedamount upon Invoice Finalization
'''

class Company(CustomBase):

	__tablename__ = 'company'

	name = Column(String(255))
	addressline1 = Column(String(255))
	addressline2 = Column(String(255))
	addressline3 = Column(String(255))
	invoices = relationship('Invoice', backref='company', lazy='dynamic')

class Customer(CustomBase):

	__tablename__ = 'customer'

	name = Column(String(255))
	addressline1 = Column(String(255))
	addressline2 = Column(String(255))
	addressline3 = Column(String(255))
	invoices = relationship('Invoice', backref='customer', lazy='dynamic')

class Project(CustomBase):

	__tablename__ = 'project'

	ixproject = Column(Integer, unique=True)
	sproject = Column(String(255))
	milestones = relationship('Milestone', backref='project', lazy='dynamic')

	def __init__(self, ixproject, sproject):
		self.ixproject = ixproject
		self.sproject = sproject

class Milestone(CustomBase):

	__tablename__ = 'milestone'

	ixfixfor = Column(Integer, unique=True)
	ixproject = Column(Integer, ForeignKey('project.ixproject'), nullable=False)
	sfixfor = Column(String(255), nullable=False)
	dtstart = Column(DateTime, nullable=True)
	dt = Column(DateTime, nullable=False)
	bfrozen = Column(Boolean, default=False)
	invoice_id = Column(Integer, ForeignKey('invoice.id'), nullable=True)
	binvoiced = Column(Boolean, default=False)
	finvoicedamount = Column(Float, nullable=True)
	bpaid = Column(Boolean, default=False)
	dtpaid = Column(DateTime, nullable=True)
	fpaidamount = Column(Float, nullable=True)
	cases = relationship('Case', backref='milestone', lazy='dynamic')
	categories = relationship('Category', backref='milestone', lazy='dynamic')

	def __init__(self, ixfixfor, sfixfor, ixproject, dt, dtstart):
		self.ixfixfor = ixfixfor
		self.sfixfor = sfixfor
		self.ixproject = ixproject
		self.dt = dt
		self.dtstart = dtstart

	def bfrozen_label_class(self):
		return "info" if self.bfrozen else "default"

	def invoiced_label_class(self):
		return "info" if self.invoice else "default"

	def bpaid_label_class(self):
		return "info" if self.bpaid else "default"

	def billable_cost(self):

		non_comped_non_deliverable_case_cost = sum([ c.cost() for c in self.cases if (not c.fogbugzusercases[0].bcomped and not c.deliverable) ])
		
		return non_comped_non_deliverable_case_cost

	def deliverables(self):
		return set([ c.deliverable for c in self.cases if c.deliverable ])

	def get_categories(self, include_empty_categories=True):
		categories = self.categories
		if not include_empty_categories:
			categories = [ c for c in categories if c.cases.count() > 0 ]

		return categories

	def uncategorized_cases(self, include_zero_cost=True):
		cases = self.cases.filter(Case.category_id==None)
		if not include_zero_cost:
			cases = [ c for c in cases if c.cost() > 0 ]

		return cases

	def no_charge_cases(self):
		cases = [ c for c in self.cases if c.cost() == 0 ]
		return cases

	def comped_cases(self):

		cases = [ c for c in self.cases if c.fogbugzusercases[0].bcomped ]
		return cases

	def cost(self):
		''' Case cost rollup '''

		return sum([ c.cost() for c in self.cases ])
		
class Case(CustomBase):

	__tablename__ = 'fbcase'

	ixbug = Column(Integer, unique=True)
	ixfixfor = Column(Integer, ForeignKey('milestone.ixfixfor'))
	stitle = Column(String(255), nullable=False)
	scategory = Column(String(255), nullable=False)
	sticket = Column(String(255), nullable=False)
	ixpriority = Column(Integer)
	sstatus = Column(String(255))
	ixpersonresolvedby = Column(Integer, ForeignKey('fogbugzuser.ixperson'), nullable=True)
	fogbugzusercases = relationship('FogbugzUserCase', backref='case', lazy='dynamic')
	category_id = Column(Integer, ForeignKey('category.id'), nullable=True)
	deliverable_id = Column(Integer, ForeignKey('deliverable.id'), nullable=True)

	def __init__(self, ixbug, ixfixfor, stitle, ixpriority, sstatus, scategory, sticket, ixpersonresolvedby):
		self.ixbug = ixbug
		self.ixfixfor = ixfixfor
		self.stitle = stitle
		self.ixpriority = ixpriority
		self.sstatus = sstatus
		self.scategory = scategory
		self.sticket = sticket
		self.ixpersonresolvedby = ixpersonresolvedby

		#self.ixpersonresolvedby = int(c.ixpersonresolvedby.string)
		#self.hrsElapsed = float(c.hrselapsed.string)
		#self.hrsElapsedExtra = float(c.hrselapsedextra.string)

	def cost(self):
		''' Billable amount for a particular employee's time on this case '''
		# -- TODO: we assume there is only one FBUC
		return self.fogbugzusercases[0].cost()

	def ticket_url(self):
		if not g.print_view:
			return "<a href='%s%s?%s' target='_blank' title=\"%s\">%s</a>" %(app.config['FOGBUGZ_URL'], app.config['CASE_ENDPOINT'], self.sticket, self.stitle, self.ixbug)
		else:
			return "%s" % self.ixbug

class FogbugzUser(CustomBase):

	__tablename__ = 'fogbugzuser'

	ixperson = Column(Integer, unique=True)
	sfullname = Column(String(255), nullable=False)
	frate = Column(Float, nullable=False, default=0.0)
	cases = relationship('Case', backref='fogbugzuser', lazy='dynamic')
	fogbugzusercases = relationship('FogbugzUserCase', backref='fogbugzuser', lazy='dynamic')

	def __init__(self, ixperson, sfullname):
		self.ixperson = ixperson
		self.sfullname = sfullname

class FogbugzUserCase(CustomBase):

	__tablename__ = 'fogbugzusercase'

	ixperson = Column(Integer, ForeignKey('fogbugzuser.ixperson'))
	ixbug = Column(Integer, ForeignKey('fbcase.ixbug'))
	bcomped = Column(Boolean, nullable=False, server_default='f')
	fhours = Column(Float, nullable=False, default=0.0)
	fhours_override = Column(Float, nullable=False, default=0.0)
	frate_override = Column(Float, nullable=False, default=0.0)

	def __init__(self, ixperson, ixbug, fhours):
		self.ixperson = ixperson
		self.ixbug = ixbug
		self.fhours = fhours

	def cost(self):
		rate = self.frate_override if self.frate_override > 0 else self.fogbugzuser.frate
		hours = self.fhours_override if self.fhours_override > 0 else self.fhours
		cost = hours*rate
		rounded_cost = float("%.2f" % (cost))

		#app.logger.info(cost - rounded_cost)
		return rounded_cost

class Category(CustomBase):

	__tablename__ = 'category'

	milestone_id = Column(Integer, ForeignKey('milestone.id'), nullable=False)
	cases = relationship('Case', backref='category', lazy='dynamic')
	name = Column(String(255), nullable=False)

	def __init__(self, name, milestone_id):
		self.name = name
		self.milestone_id = milestone_id

	def cost(self):
		return sum([ c.cost() for c in self.cases ])

class Deliverable(CustomBase):

	__tablename__ = 'deliverable'

	cases = relationship('Case', backref='deliverable', lazy='dynamic')
	name = Column(String(255), nullable=False)
	festimate = Column(Float, nullable=False, server_default='0.0')
	frefunded = Column(Float, nullable=False, server_default='0.0')
	binvoiced = Column(Boolean, nullable=False, server_default='f')
	bpaid = Column(Boolean, nullable=False, server_default='f')
	invoice_id = Column(Integer, ForeignKey('invoice.id'), nullable=True)
	refund_invoice_id = Column(Integer, ForeignKey('invoice.id'), nullable=True)

	def __init__(self, name, festimate):
		self.name = name
		self.festimate = festimate

	def editable(self):
		return (not self.invoice or not self.invoice.state == 'final') \
			and (not self.refund_invoice or not self.refund_invoice.state == 'final')

	def refundable(self):
		return self.invoice and self.invoice.state == 'final' and self.frefunded == 0 and self.balance() != 0

	def balance(self):
		b = self.festimate - self.frefunded - sum([ c.cost() for c in self.cases if not c.fogbugzusercases[0].bcomped ])
		# -- sometimes a fraction of a cent will keep the balance open
		# -- actually with the rounded_cost fix in FogbugzUserCase.cost() this may no longer be an issue
		if abs(b) < 0.01:
			app.logger.warn('Deliverable.balance() reports a value less than a penny - trunced to zero')
			b = 0

		return b

	def cases_in_milestone(self, milestone):
		''' The intersection of the deliverable's cases and the given milestone's cases '''
		return [ c for c in self.cases if c in milestone.cases ]

	def cost_in_milestone(self, milestone):
		''' Billable amount of the intersection of the deliverable's cases and the given milestone's cases '''
		return sum([ c.cost() for c in self.cases if c in milestone.cases ])

class Invoice(CustomBase):

	__tablename__ = 'invoice'

	company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
	customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
	state = Column(String(20), nullable=False, server_default='final')
	milestones = relationship('Milestone', backref='invoice', lazy='dynamic')
	unpaid_deliverables = relationship('Deliverable', foreign_keys=[Deliverable.invoice_id], backref='invoice', lazy='dynamic')
	refund_deliverables = relationship('Deliverable', foreign_keys=[Deliverable.refund_invoice_id], backref='refund_invoice', lazy='dynamic')

	def billable_cost(self):

		return sum([ m.billable_cost() for m in self.milestones.all() ]) + sum([ d.festimate for d in self.unpaid_deliverables ]) - sum([ d.frefunded for d in self.refund_deliverables ]) 

class Payment(CustomBase):

	__tablename__ = 'payment'

	famount = Column(Float, nullable=False, server_default='0.0')
	date_deposited = Column(Date, nullable=False, server_default=text('current_date'))
	customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
	company_id = Column(Integer, ForeignKey('company.id'), nullable=False)

class InvoicePayment(CustomBase):

	__tablename__ = 'invoicepayment'

	invoice_id = Column(Integer, ForeignKey('invoice.id'), nullable=False)
	payment_id = Column(Integer, ForeignKey('payment.id'), nullable=False)
	famount_apportioned = Column(Float, nullable=False, server_default='0.0')
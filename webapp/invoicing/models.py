from sqlalchemy import Column, func, String, SmallInteger, Integer, DateTime, Boolean, Float
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship
from webapp.models import CustomBase
from flask import g

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

	def billable_cost(self):

		comped_case_cost = sum([ float(c.fogbugzusercases[0].cost()) for c in self.cases if c.fogbugzusercases[0].bcomped ])
		deliverable_cost = sum([ float(d.cost_in_milestone(self)) for d in self.deliverables() ])

		return "%.2f" % (float(self.cost()) - comped_case_cost - deliverable_cost)

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
			cases = [ c for c in cases if float(c.fogbugzusercases[0].cost()) > 0 ]

		return cases

	def no_charge_cases(self):
		cases = [ c for c in self.cases if float(c.fogbugzusercases[0].cost()) == 0 ]
		return cases

	def comped_cases(self):

		cases = [ c for c in self.cases if c.fogbugzusercases[0].bcomped ]
		return cases

	def cost(self):

		return "%.2f" % sum([ float(c.fogbugzusercases[0].cost()) for c in self.cases ])
		
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

	def ticket_url(self):
		if not g.print_view:
			return "<a href='https://palkosoftware.fogbugz.com/default.asp?%s' target='_blank' title=\"%s\">%s</a>" %(self.sticket, self.stitle, self.ixbug)
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

		return "%.2f" % (hours*rate)

class Category(CustomBase):

	__tablename__ = 'category'

	milestone_id = Column(Integer, ForeignKey('milestone.id'), nullable=False)
	cases = relationship('Case', backref='category', lazy='dynamic')
	name = Column(String(255), nullable=False)

	def __init__(self, name, milestone_id):
		self.name = name
		self.milestone_id = milestone_id

	def cost(self):
		return "%.2f" % sum([ float(c.fogbugzusercases[0].cost()) for c in self.cases ])

class Deliverable(CustomBase):

	__tablename__ = 'deliverable'

	cases = relationship('Case', backref='deliverable', lazy='dynamic')
	name = Column(String(255), nullable=False)
	festimate = Column(Float, nullable=False, server_default='0.0')
	binvoiced = Column(Boolean, nullable=False, server_default='f')
	bpaid = Column(Boolean, nullable=False, server_default='f')

	def __init__(self, name, festimate):
		self.name = name
		self.festimate = festimate

	def balance(self):
		return self.festimate - sum([ float(c.fogbugzusercases[0].cost()) for c in self.cases if not c.fogbugzusercases[0].bcomped ])

	def cases_in_milestone(self, milestone):
		return [ c for c in self.cases if c in milestone.cases ]

	def cost_in_milestone(self, milestone):
		return "%.2f" % sum([ float(c.fogbugzusercases[0].cost()) for c in self.cases if c in milestone.cases ])

class Invoice(CustomBase):

	__tablename__ = 'invoice'

	company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
	customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
	milestones = relationship('Milestone', backref='invoice', lazy='dynamic')

	def billable_cost(self):
		return "%.2f" %(sum([ float(m.billable_cost()) for m in self.milestones.all() ]))
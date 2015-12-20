from sqlalchemy import Column, func, String, SmallInteger, Integer, DateTime
from webapp.models import CustomBase

class FixFor(CustomBase):

	__abstract__  = True
	__tablename__ = 'fixfor'

	def __init__(self, ixFixFor, sFixFor, ixProject, sProject, dt, dtStart):
		self.ixFixFor = ixFixFor
		self.sFixFor = sFixFor
		self.ixProject = ixProject
		self.sProject = sProject
		self.dt = dt
		self.dtStart = dtStart
		self.cases = []
		self.person_hours = {}
		self.total_hours = 0
		self.cost = 0

class Case(CustomBase):

	__abstract__  = True
	__tablename__ = 'case'

	def __init__(self, c):
		self.ixPersonResolvedBy = int(c.ixpersonresolvedby.string)
		self.hrsElapsed = float(c.hrselapsed.string)
		self.hrsElapsedExtra = float(c.hrselapsedextra.string)

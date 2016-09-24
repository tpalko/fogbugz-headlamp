from webapp import app, logger
from fogbugz import FogBugz, FogBugzConnectionError

class FogBugzClient:

	fb = None
	person_cache = {}

	def __init__(self):

	    logger.info("Signing into FogBugz at %s with %s:%s" %(app.config['FOGBUGZ_URL'], app.config['FOGBUGZ_ACCOUNT_NAME'], app.config['FOGBUGZ_PASSWORD']))

	    try:
	        self.fb = FogBugz(app.config['FOGBUGZ_URL'])
	        self.fb.logon(app.config['FOGBUGZ_ACCOUNT_NAME'], app.config['FOGBUGZ_PASSWORD'])
	    except (FogBugzConnectionError, AttributeError,) as fbce:
	        logger.error(str(fbce)) 
	        #raise Exception("App cannot start without FogBugz!")
	
	'''
	def get_fixfor_by_id(ixfixfor, fixfors):

		my_fixfor = [ f for f in fixfors if f.ixfixfor == ixixfor ]
		return my_fixfor[0] if any(my_fixfor) else None
	'''

	def get_person(self, ixperson):
		if ixperson is None or int(ixperson) == 0:
			return None

		if ixperson not in self.person_cache:
			response = self.fb.viewPerson(ixperson=ixperson)
			self.person_cache[ixperson] = response.person

		return self.person_cache[ixperson]

	'''
	def get_project_name(ixproject):
		if ixproject is None or int(ixproject) == 0:
			return None

		if ixproject not in project_names:
			response = self.fb.viewProject(ixproject=ixproject)
			project_names[ixproject] = parse_cdata(response.project)
	'''

	def get_projects(self):
		return self.fb.listProjects()

	def get_fixfors(self):
		return self.fb.listFixFors()

	def search(self, q="", cols=""):
		return self.fb.search(q=q, cols=cols)
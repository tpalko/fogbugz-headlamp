#?token=quadespiooa20s5ghq507mkegula65


from flask import Flask
from flask import render_template
from flask import request
from fogbugz import FogBugz
import re
from datetime import datetime

app = Flask(__name__)
app.debug = True

fb = FogBugz("https://palkosoftware.fogbugz.com") 
fb.logon("tim@palkosoftware.com", "Ilmgitmn8")

person_names = {}

rates = {'Tim Palko': 85, 'Aaron Volkmann': 85, 'Darren Slimick': 20, 'Howard Jackson': 85, 'Rick McNerny': 0, 'Dave Kleinschmidt': 85}

class fixfor():

	def __init__(self, ixFixFor, sFixFor, ixProject, sProject, dt, dtStart):
		self.ixFixFor = ixFixFor
		self.sFixFor = sFixFor
		self.ixProject = ixProject
		self.sProject = sProject
		self.dt = dt
		self.dtStart = dtStart
		self.cases = []
		self.person_hours = {}
		self.cost = 0

class case():

	def __init__(self, ixPersonResolvedBy, hrsElapsed, hrsElapsedExtra):
		self.ixPersonResolvedBy = int(ixPersonResolvedBy)
		self.hrsElapsed = float(hrsElapsed)
		self.hrsElapsedExtra = float(hrsElapsedExtra)

def get_fixfor_by_id(ixfixfor, fixfors):

	for f in fixfors:
		if f.ixFixFor == ixfixfor:
			return f

	return None

def parse_cdata(string):
	return re.sub('\[CDATA\]', '', string)

def get_person_name(ixPerson):

	if ixPerson not in person_names:
		response = fb.viewPerson(ixPerson=ixPerson)		
		person_names[ixPerson] = parse_cdata(response.person.sfullname.string)
	
	return person_names[ixPerson]

@app.route('/')
def milestones():

	filter = request.args.get('filter', None)

	fixforlist = fb.listFixFors()

	fixfors = []
	now = datetime.now()

	total_cost = 0

	for f in fixforlist.findAll('fixfor'):

		if f.dt.string is None:
			continue
		
		sfixfor = parse_cdata(f.sfixfor.contents[0]) if len(f.sfixfor.contents) > 0 else "-"

		if filter is not None and filter not in sfixfor:
			continue

		startdate = None

		# -- 2013-10-03T04:00:00Z	
		if f.dtstart.string is not None:
			startdate = datetime.strptime(f.dtstart.string, "%Y-%m-%dT%H:%M:%SZ")

		enddate = datetime.strptime(f.dt.string, "%Y-%m-%dT%H:%M:%SZ")

		if enddate < now:

			fixfors.append(fixfor(
					f.ixfixfor.string, 				
					sfixfor,
					f.ixproject.string, 
					parse_cdata(f.sproject.contents[0]) if len(f.sproject.contents) > 0 else "-",
					enddate, 
					startdate))

	caselist = fb.search(q="", cols="ixFixFor,ixProject,sStatus,ixPersonResolvedBy,hrsElapsed,hrsElapsedExtra")

	description_tag = caselist.find("description")	

	description = parse_cdata(description_tag.string)

	for c in caselist.findAll('case'):

		if c.ixfixfor is None:
			continue

		if not c.sstatus.contents[0].find("Resolved") and not c.sstatus.contents[0].find("Closed"):
			continue

		f = get_fixfor_by_id(c.ixfixfor.string, fixfors)
		
		if f is not None:

			f.cases.append(case(
				c.ixpersonresolvedby.string,
				c.hrselapsed.string,
				c.hrselapsedextra.string)
			)

	for f in fixfors:
		
		for c in f.cases:

			person_name = get_person_name(c.ixPersonResolvedBy)				

			if person_name not in f.person_hours:				
				f.person_hours[person_name] = 0

			f.person_hours[person_name] += c.hrsElapsed
			f.cost += c.hrsElapsed*rates[person_name]

		total_cost += f.cost

	fixfors = sorted(fixfors, key=lambda fixfor: fixfor.dt, reverse=True)

	return render_template('milestones.html', filter=filter, total_cost=total_cost, description=description, fixfors=fixfors)

if __name__ == "__main__":
	app.run()
#?token=quadespiooa20s5ghq507mkegula65

import sys
from flask import Flask
from flask import render_template
from flask import request
from fogbugz import FogBugz
import re
from datetime import datetime
import traceback
import logging

logging.basicConfig(level=logging.DEBUG)

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

	if ixPerson is None or int(ixPerson) == 0:
		return None

	if ixPerson not in person_names:
		response = fb.viewPerson(ixPerson=ixPerson)		
		person_names[ixPerson] = parse_cdata(response.person.sfullname.string)
	
	return person_names[ixPerson]

@app.route('/', methods=['GET', 'POST'])
def milestones():

	try:

		milestone_filter = None
		person_filter = None
		lastmilestone_filter = None

		if request.method == "POST":
			milestone_filter = request.form['milestone_filter'] if request.form['milestone_filter'] != "" else ""
			person_filter = request.form['person_filter'] if request.form['person_filter'] != "" else None
			lastmilestone_filter = request.form['lastmilestone_filter'] if request.form['lastmilestone_filter'] != "" else None

		fixforlist = fb.listFixFors()

		#logging.debug(fixforlist.prettify())

		fixfors = []
		milestones_filter = []
		now = datetime.now()
		cutoff = now

		if lastmilestone_filter is not None and lastmilestone_filter != "":
			lastmilestone = fixforlist.findAll(text=re.compile("^%s$" %(lastmilestone_filter)))
			if len(lastmilestone) > 0:
				cutoff = datetime.strptime(lastmilestone[0].parent.parent.dt.string, "%Y-%m-%dT%H:%M:%SZ")
				logging.debug(cutoff)

		total_cost = 0

		for f in fixforlist.findAll('fixfor'):

			if f.dt.string is None:
				continue
			
			sfixfor = parse_cdata(f.sfixfor.contents[0]) if len(f.sfixfor.contents) > 0 else "-"

			if milestone_filter is not None and milestone_filter not in sfixfor:
				continue

			startdate = None

			# -- 2013-10-03T04:00:00Z	
			if f.dtstart.string is not None:
				startdate = datetime.strptime(f.dtstart.string, "%Y-%m-%dT%H:%M:%SZ")

			enddate = datetime.strptime(f.dt.string, "%Y-%m-%dT%H:%M:%SZ")

			milestones_filter.append(fixfor(
				f.ixfixfor.string, 				
				sfixfor,
				f.ixproject.string, 
				parse_cdata(f.sproject.contents[0]) if len(f.sproject.contents) > 0 else "-",
				enddate, 
				startdate))

			# - we're invoicing whole milestones, so we don't want to factor in milestones that haven't ended yet
			if enddate <= cutoff:

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

		# - find all relevant cases
		for c in caselist.findAll('case'):

			if c.ixfixfor is None:
				continue

			if not c.sstatus.contents[0].find("Resolved") and not c.sstatus.contents[0].find("Closed"):
				continue

			f = get_fixfor_by_id(c.ixfixfor.string, fixfors)
			
			if f is None:
				continue

			if person_filter is not None and int(c.ixpersonresolvedby.string) != int(person_filter):
				continue

			f.cases.append(case(
				c.ixpersonresolvedby.string,
				c.hrselapsed.string,
				c.hrselapsedextra.string)
			)

		# - for each case in each milestone, figure hours per person per case, and total cost for the milestone
		for f in fixfors:
			
			for c in f.cases:

				person_name = get_person_name(c.ixPersonResolvedBy)				

				if person_name is None:
					continue
					
				if person_name not in f.person_hours:				
					f.person_hours[person_name] = 0

				f.person_hours[person_name] += c.hrsElapsed
				f.cost += c.hrsElapsed*rates[person_name]

			total_cost += f.cost

		fixfors = sorted(fixfors, key=lambda fixfor: fixfor.dt, reverse=True)
		milestones_filter = sorted(milestones_filter, key=lambda fixfor: fixfor.dt, reverse=True)

		return render_template('milestones.html', person_names=person_names, milestones_filter=milestones_filter, milestone_filter=milestone_filter, person_filter=person_filter, lastmilestone_filter=lastmilestone_filter, total_cost=total_cost, description=description, fixfors=fixfors)

	except:
		
		print sys.exc_info()
		traceback.print_tb(sys.exc_info()[2])
		return render_template('error.html', error=sys.exc_info()[2])

if __name__ == "__main__":
	app.run()

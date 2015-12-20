# ?token=quadespiooa20s5ghq507mkegula65

import os
import sys
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.ext.login import login_required
from fogbugz import FogBugz
import re
from datetime import datetime
import traceback
import ConfigParser
from .models import FixFor, Case
from webapp import app, logger

fb = FogBugz(app.config['FOGBUGZ_URL'])
fb.logon(app.config['FOGBUGZ_ACCOUNT_NAME'], app.config['FOGBUGZ_PASSWORD'])

invoicing = Blueprint('invoicing', __name__, url_prefix='/invoicing')

def parse_cdata(string):
	return re.sub('\[CDATA\]', '', string)

project_names = {}
person_names = {}

projects = fb.listProjects().findAll("project")

for p in projects:
	project_names[p.ixproject.string] = parse_cdata(p.sproject.string)

# - 'names' is a comma-delimited list of user names as they appear in your Fogbugz configuration
billing_names = app.config['BILLING_NAMES'].split(',')
# - 'rates' is a comma-delimited list of hourly rates at which each user in the 'names' list bills out, respectively
billing_rates = app.config['BILLING_RATES'].split(',')

rates = dict(zip(billing_names, billing_rates))

def get_fixfor_by_id(ixfixfor, fixfors):
	for f in fixfors:
		if f.ixFixFor == ixfixfor:
			return f

	return None

def get_person_name(ixPerson):
	if ixPerson is None or int(ixPerson) == 0:
		return None

	if ixPerson not in person_names:
		response = fb.viewPerson(ixPerson=ixPerson)
		person_names[ixPerson] = parse_cdata(response.person.sfullname.string)

	return person_names[ixPerson]

def get_project_name(ixProject):
	if ixProject is None or int(ixProject) == 0:
		return None

	if ixProject not in project_names:
		response = fb.viewProject(ixProject=ixProject)
		project_names[ixProject] = parse_cdata(response.project)

@invoicing.route('/', methods=['GET', 'POST'])
@login_required
def milestones():
	try:

		milestone_filter = None
		person_filter = None
		project_filter = None
		start_milestone = None
		end_milestone = None
		single_milestone = False

		if request.method == "POST":
			milestone_filter = request.form['milestone_filter'] if request.form['milestone_filter'] != "" else ""
			person_filter = request.form['person_filter'] if request.form['person_filter'] != "" else None
			project_filter = int(request.form['project_filter']) if request.form['project_filter'] != "" else None
			start_milestone = request.form['start_milestone'] if request.form['start_milestone'] != "" else None
			end_milestone = request.form['end_milestone'] if request.form['end_milestone'] != "" else None
		#single_milestone = bool(request.form['single_milestone']) if 'single_milestone' in request.form else False

		fixforlist = fb.listFixFors()

		fixfors = []
		milestones_filter = []
		now = datetime.now()
		start_cutoff = datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
		end_cutoff = now

		if start_milestone is not None and start_milestone != "":
			start_fixfor = fixforlist.findAll(text=re.compile("^%s$" % (start_milestone)))
			if len(start_fixfor) > 0:
				start_cutoff = datetime.strptime(start_fixfor[0].parent.parent.dt.string, "%Y-%m-%dT%H:%M:%SZ")
				logging.debug("start cutoff %s" % start_cutoff)

		if end_milestone is not None and end_milestone != "":
			end_fixfor = fixforlist.findAll(text=re.compile("^%s$" % (end_milestone)))
			if len(end_fixfor) > 0:
				end_cutoff = datetime.strptime(end_fixfor[0].parent.parent.dt.string, "%Y-%m-%dT%H:%M:%SZ")
				logging.debug("end cutoff %s" % end_cutoff)

		total_hours = 0
		total_cost = 0

		# - build milestone filter lists for user selection and populate initial result milestone list
		for f in fixforlist.findAll('fixfor'):

			logger.debug(f)

			if f.dt.string is None:
				continue

			sfixfor = parse_cdata(f.sfixfor.contents[0]) if len(f.sfixfor.contents) > 0 else "-"

			if milestone_filter is not None and milestone_filter not in sfixfor:
				continue

			if f.ixproject.string:

				ixproject = int(f.ixproject.string)

				if project_filter is not None and project_filter != ixproject:
					continue
			else:
				# - we have a project filter, and this milestone does not belong to a project
				if project_filter:
					continue

			startdate = None

			# -- 2013-10-03T04:00:00Z	
			if f.dtstart.string is not None:
				startdate = datetime.strptime(f.dtstart.string, "%Y-%m-%dT%H:%M:%SZ")

			enddate = datetime.strptime(f.dt.string, "%Y-%m-%dT%H:%M:%SZ")

			milestones_filter.append(FixFor(
				f.ixfixfor.string,
				sfixfor,
				f.ixproject.string,
				parse_cdata(f.sproject.contents[0]) if len(f.sproject.contents) > 0 else "-",
				enddate,
				startdate))

			# - we're invoicing whole milestones, so we don't want to factor in milestones that haven't ended yet
			if enddate <= end_cutoff and enddate >= start_cutoff:
				fixfors.append(FixFor(
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

			if project_filter is not None and int(c.ixproject.string) != int(project_filter):
				continue

			f.cases.append(Case(c))

		# - for each case in each milestone, figure hours per person per case, and total cost for the milestone
		for f in fixfors:

			for c in f.cases:

				person_name = get_person_name(c.ixPersonResolvedBy)
				#logger.debug(c)
				#project_name = get_project_name(c.ixproject)

				if person_name is None:
					continue

				rate = float(rates[person_name])

				if rate == 0:
					continue

				if person_name not in f.person_hours:
					f.person_hours[person_name] = 0

				f.person_hours[person_name] += c.hrsElapsed
				f.total_hours += c.hrsElapsed
				f.cost += c.hrsElapsed * rate

			total_hours += f.total_hours
			total_cost += f.cost

		fixfors = sorted(fixfors, key=lambda fixfor: fixfor.dt, reverse=True)
		milestones_filter = sorted(milestones_filter, key=lambda fixfor: fixfor.dt, reverse=True)

		return render_template('invoicing/milestones.html', person_names=person_names, project_names=project_names,
							   milestones_filter=milestones_filter, milestone_filter=milestone_filter,
							   person_filter=person_filter, project_filter=project_filter,
							   start_milestone=start_milestone, end_milestone=end_milestone,
							   single_milestone=single_milestone, total_hours=total_hours, total_cost=total_cost,
							   description=description, fixfors=fixfors)

	except:

		print sys.exc_info()
		traceback.print_tb(sys.exc_info()[2])
		return render_template('error.html', error=sys.exc_info()[2])


# ?token=quadespiooa20s5ghq507mkegula65

import os
import sys
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, json
from flask.ext.login import login_required
import re
from datetime import datetime
import traceback
import ConfigParser
from .models import Project, Milestone, Case, FogbugzUser, FogbugzUserCase, Category, Deliverable, Invoice, Company, Customer
from .forms import DeliverableForm, PaymentForm
from webapp import app, logger
from sqlalchemy import text

invoicing = Blueprint('invoicing', __name__, url_prefix='/invoicing')

def parse_cdata(string):
	return re.sub('\[CDATA\]', '', string)

# - 'names' is a comma-delimited list of user names as they appear in your Fogbugz configuration
billing_names = app.config['BILLING_NAMES'].split(',')
# - 'rates' is a comma-delimited list of hourly rates at which each user in the 'names' list bills out, respectively
billing_rates = app.config['BILLING_RATES'].split(',')

rates = dict(zip(billing_names, billing_rates))

def get_date_from_iso(iso_string):
	# -- 2013-10-03T04:00:00Z	
	if iso_string:
		return datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%SZ")
	return None

def warn_and_flash(message):
	logger.warn(message)
	flash(message)

@invoicing.route('/refresh', methods=['GET'])
@login_required
def refresh():

	try:

		from .fogbugz_client import FogBugzClient

		fbc = FogBugzClient()

		if not fbc.test_connection():
			raise Exception("Failed to get a FogBugz client going")

		now = datetime.now()

		projectlist = fbc.get_projects()

		for p in projectlist.findAll("project"):

			existing_project = g.db.query(Project).filter(Project.ixproject==int(p.ixproject.string)).first()

			if existing_project:
				
				if existing_project.sproject != p.sproject.string:
					logger.info("Updating project name %s -> %s" %(existing_project.sproject, p.sproject.string))
					existing_project.sproject = p.sproject.string
					g.db.commit()

			else:
				new_project = Project(int(p.ixproject.string), p.sproject.string)
				g.db.add(new_project)
				g.db.commit()				
				logger.info("Added new project %s" % new_project.sproject)

		fixforlist = fbc.get_fixfors()

		for f in fixforlist.findAll('fixfor'):

			sfixfor = parse_cdata(f.sfixfor.contents[0]) if len(f.sfixfor.contents) > 0 else "-"
			#sproject = parse_cdata(f.sproject.contents[0]) if len(f.sproject.contents) > 0 else "-"
			startdate = get_date_from_iso(f.dtstart.string)
			enddate = get_date_from_iso(f.dt.string)

			if not enddate:
				logger.info("Milestone %s has no end date - skipping" %(sfixfor))
				continue

			existing_milestone = g.db.query(Milestone).filter(Milestone.ixfixfor==int(f.ixfixfor.string)).first()
			
			if existing_milestone:
				if existing_milestone.bfrozen:
					# - it's frozen, so don't commit anything, but we want to know if it's been changed significantly w.r.t. billing
					if enddate > now:
						warn_and_flash("Frozen milestone %s now ends in the future" % existing_milestone.sfixfor)
				else:
					if existing_milestone.sfixfor != sfixfor or existing_milestone.dt != enddate or existing_milestone.dtstart != startdate:
						logger.info("Milestone %s metadata has changed - updating" %(existing_milestone.project.sproject))
						existing_milestone.update(ixfixfor=int(f.ixfixfor.string), sfixfor=sfixfor, ixproject=int(f.ixproject.string), dt=enddate, dtstart=startdate)
						g.db.add(existing_milestone)
						g.db.commit()
					else:
						logger.info("Milestone %s - no change" %(existing_milestone.sfixfor))
			else:
				if enddate > now:
					logger.info("New Milestone %s in future - skipping" %(sfixfor))
					continue

				new_milestone = Milestone(int(f.ixfixfor.string), sfixfor, int(f.ixproject.string), enddate, startdate)
				g.db.add(new_milestone)
				g.db.commit()
				logger.info("Added new milestone %s" % new_milestone.sfixfor)
		
		caselist = fbc.search(cols="ixBug,ixPriority,sCategory,sTicket,sTitle,ixFixFor,ixProject,sStatus,ixPersonResolvedBy,hrsElapsed,hrsElapsedExtra")

		#description_tag = caselist.find("description")

		#description = parse_cdata(description_tag.string)

		# - find all relevant cases
		for c in caselist.findAll('case'):

			#logger.debug("Case %s status %s" %(c.ixbug.string, c.sstatus.string))

			fb_case = g.db.query(Case).filter(Case.ixbug==int(c.ixbug.string)).first()
			milestone = g.db.query(Milestone).filter(Milestone.ixfixfor==int(c.ixfixfor.string)).first()

			if c.sstatus.string.find("Resolved") < 0 and c.sstatus.string.find("Closed") < 0:
				logger.info("Case %s not resolved or closed - skipping" %(c.ixbug.string))
				if fb_case:
					logger.info("Case %s imported previously, but has since been reopened" % c.ixbug.string)
					if milestone and milestone.bfrozen:
						warn_and_flash("Case %s reopened on frozen milestone!" % c.ixbug.string)
					else:
						g.db.delete(fb_case)
						g.db.commit()
				continue
			
			if not milestone:
				warn_and_flash("No milestone found for case %s, cannot bill - skipping" % c.ixbug.string)
				continue

			person = None
			fogbugz_user = None

			if int(c.ixpersonresolvedby.string) > 0:
				person = fbc.get_person(c.ixpersonresolvedby.string)
			
			if person:
				fogbugz_user = g.db.query(FogbugzUser).filter(FogbugzUser.ixperson==int(person.ixperson.string)).first()
			else:
				warn_and_flash("Case %s resolved or closed by UNKNOWN entity (%s), cannot bill - skipping" %(c.ixbug.string, c.ixpersonresolvedby.string))
				continue

			if not fogbugz_user and person:
				fogbugz_user = FogbugzUser(ixperson=int(person.ixperson.string), sfullname=person.sfullname.string)
				g.db.add(fogbugz_user)
				g.db.commit()
				logger.info("Added new FogBugz user %s" % fogbugz_user.sfullname)

			if fogbugz_user and fogbugz_user.sfullname in rates and float(fogbugz_user.frate) != float(rates[fogbugz_user.sfullname]):

				if milestone.bfrozen:
					warn_and_flash("Case-Resolving User's rate changed on frozen milestone!")
				else:
					logger.info("%s got a raise from %.2f to %.2f" %(fogbugz_user.sfullname, float(fogbugz_user.frate), float(rates[fogbugz_user.sfullname])))
					fogbugz_user.frate = float(rates[fogbugz_user.sfullname])
					g.db.add(fogbugz_user)
					g.db.commit()							

			if fb_case:

				if fb_case.milestone.bfrozen:

					# - don't commit anything, but we want to know if it's been changed significantly w.r.t. billing

					if fb_case.stitle != c.stitle.string:
						warn_and_flash("Case %s title changed on frozen milestone (%s -> %s)" %(fb_case.ixbug, fb_case.stitle, c.stitle.string))

					if fb_case.ixfixfor != int(c.ixfixfor.string):
						warn_and_flash("Case %s moved out of frozen milestone (milestone %s -> %s)" %(fb_case.ixbug, fb_case.ixfixfor, c.ixfixfor.string))

					if fb_case.scategory != c.scategory.string:
						warn_and_flash("Case %s category changed (%s -> %s)" %(fb_case.ixbug, fb_case.scategory, c.scategory.string))

					if fb_case.sstatus != c.sstatus.string:
						warn_and_flash("Case %s status changed (%s -> %s)" %(fb_case.ixbug, fb_case.sstatus, c.sstatus.string))

					if fb_case.sticket != c.sticket.string:
						warn_and_flash("Case %s ticket changed (%s -> %s)" %(fb_case.ixbug, fb_case.sticket, c.sticket.string))

					if (c.ixpersonresolvedby.string > 0 and fb_case.ixpersonresolvedby != int(c.ixpersonresolvedby.string)):
						warn_and_flash("Case %s resolver changed (%s -> %s)" %(fb_case.ixbug, fb_case.ixpersonresolvedby, c.ixpersonresolvedby.string))

				else:
					
					logger.debug("db type: %s and fb type: %s" %(type(fb_case.ixfixfor), type(c.ixfixfor.string)))

					if fb_case.stitle != c.stitle.string \
						or fb_case.ixfixfor != int(c.ixfixfor.string) \
						or fb_case.scategory != c.scategory.string \
						or fb_case.sticket != c.sticket.string \
						or (c.ixpersonresolvedby.string > 0 and fb_case.ixpersonresolvedby != int(c.ixpersonresolvedby.string)):

							fb_case.update(
								sTitle=c.stitle.string, 
								ixpriority=int(c.ixpriority.string),
								sstatus=c.sstatus.string,
								scategory=c.scategory.string, 
								sticket=c.sticket.string, 
								ixfixfor=int(fb_case.ixfixfor))

							if int(c.ixpersonresolvedby.string) > 0:
								fb_case.update(ixpersonresolvedby=int(c.ixpersonresolvedby.string))
							
					g.db.commit()
			else:

				if milestone.bfrozen:
					warn_and_flash("New Case %s added to frozen milestone" % c.ixbug.string)
				else:
					fb_case = Case(int(c.ixbug.string), int(milestone.ixfixfor), c.stitle.string, int(c.ixpriority.string), c.sstatus.string, c.scategory.string, c.sticket.string, int(c.ixpersonresolvedby.string))
					g.db.add(fb_case)
					g.db.commit()				

			if fogbugz_user and fb_case:

				fogbugz_user_case = g.db.query(FogbugzUserCase).filter(FogbugzUserCase.ixperson==int(fogbugz_user.ixperson), FogbugzUserCase.ixbug==int(fb_case.ixbug)).first()

				if fogbugz_user_case:
					fogbugz_user_case.update(ixperson=int(fogbugz_user.ixperson), fhours=float(c.hrselapsed.string))
					g.db.commit()
				elif milestone.bfrozen:
					warn_and_flash("New Case %s added to frozen milestone!" %(fb_case.ixbug))
				else:
					fogbugz_user_case = FogbugzUserCase(ixperson=fogbugz_user.ixperson, ixbug=fb_case.ixbug, fhours=float(c.hrselapsed.string))
					g.db.add(fogbugz_user_case)
					g.db.commit()

	except:
		logger.error(str(sys.exc_info()[0]))
		logger.error(str(sys.exc_info()[1]))
		traceback.print_tb(sys.exc_info()[2])
		
		flash(str(sys.exc_info()[1]))

	return redirect(url_for('invoicing.milestones'))

@invoicing.route('/milestone/<milestone_id>', methods=['POST'])
@login_required
def milestone_update(milestone_id):

	action = request.form['action']
	milestone = g.db.query(Milestone).get(milestone_id)

	if action == 'toggle_freeze':
		milestone.bfrozen = not milestone.bfrozen
		g.db.commit()

	return render_template('invoicing/_milestone_status_and_buttons.html', milestone=milestone)

@invoicing.route('/milestone/<milestone_id>', methods=['GET'])
@login_required
def milestone_detail(milestone_id):

	milestone = g.db.query(Milestone).get(milestone_id)
	categories = g.db.query(Category).distinct(Category.name).order_by(Category.name)
	open_deliverables = g.db.query(Deliverable).all()

	uncategorized_case_detail = get_uncategorized_case_detail(milestone)

	milestone_cases = g.db.query(Case).from_statement(text("select distinct c.*, fuc.fhours \
		from fbcase c \
		left join fogbugzusercase fuc on fuc.ixbug = c.ixbug \
		where c.ixfixfor = :ixfixfor \
		order by c.ixpriority, fuc.fhours desc")).params(ixfixfor=milestone.ixfixfor).all()

	#milestone_cases = g.db.query(Case).filter(Case.ixfixfor==milestone.ixfixfor).order_by(Case.fogbugzusercases.fhours, Case.category_id.desc())

	return render_template('invoicing/milestone_detail.html', 
		milestone=milestone, 
		categories=categories, 
		open_deliverables=open_deliverables,
		uncategorized_case_cost=uncategorized_case_detail['cost'], 
		uncategorized_case_count=uncategorized_case_detail['count'], 
		milestone_cases=milestone_cases)

def get_uncategorized_case_detail(milestone):

	uncategorized_cases = milestone.uncategorized_cases() #g.db.query(Case).filter(Case.ixfixfor==milestone.ixfixfor, Case.category_id==None)

	uncategorized_cost = "%.2f" % sum([ float(c.fogbugzusercases[0].cost()) for c in uncategorized_cases ])
	uncategorized_case_count = uncategorized_cases.count()

	return { 'cost': uncategorized_cost, 'count': uncategorized_case_count }

@invoicing.route('/milestone/<milestone_id>/category', methods=['POST'])
@login_required
def category_create(milestone_id):

	name = request.form["category_name"]
	category = Category(name, milestone_id)

	g.db.add(category)
	g.db.commit()

	return redirect(url_for('invoicing.milestone_detail', milestone_id=milestone_id))

@invoicing.route('/case/<case_id>/view', methods=['GET'])
@login_required
def case_view(case_id):
	case = g.db.query(Case).get(case_id)
	return render_template('invoicing/case_view.html', iframe_src="https://palkosoftware.fogbugz.com/default.asp?%s" % case.sticket)

@invoicing.route('/case/<case_id>/action', methods=['POST'])
@login_required
def case_action(case_id):

	case = g.db.query(Case).get(case_id)
	categories = g.db.query(Category).distinct(Category.name).order_by(Category.name)
	open_deliverables = g.db.query(Deliverable).all()

	if request.form["action"] == "comp":
		case.fogbugzusercases[0].bcomped = True
		g.db.commit()
	elif request.form["action"] == "uncomp":
		case.fogbugzusercases[0].bcomped = False
		g.db.commit()
	elif request.form["action"].find("deliverable_") == 0:
		deliverable_id = request.form["action"].split("_")[1]
		# - toggle
		case.deliverable_id = None if case.deliverable_id and int(case.deliverable_id) == int(deliverable_id) else deliverable_id
		g.db.commit()

	return render_template('invoicing/_milestone_detail_case_row.html', case=case, categories=categories, open_deliverables=open_deliverables)

@invoicing.route('/case/<case_id>', methods=['POST'])
@login_required
def case_category_create(case_id):

	case = g.db.query(Case).get(case_id)
	category_id_to_set = None

	if request.form["category_id"]:

		category_posted = g.db.query(Category).get(request.form["category_id"])

		if case.milestone.id == category_posted.milestone.id:
			category_id_to_set = category_posted.id
		else:
			category_for_milestone = g.db.query(Category).filter(Category.name==category_posted.name, Category.milestone_id==case.milestone.id).first()
			if not category_for_milestone:
				category_for_milestone = Category(category_posted.name, case.milestone.id)
				g.db.add(category_for_milestone)
				g.db.commit()
			category_id_to_set = category_for_milestone.id

	original_category = case.category
	if case.category_id != category_id_to_set:
		case.category_id = category_id_to_set

	g.db.commit()

	uncategorized_case_detail = get_uncategorized_case_detail(case.milestone)

	return_obj = {
		'category_id': case.category.id if case.category else None,
		'category_name': case.category.name if case.category else "",
		'category_case_cost': case.category.cost() if case.category else 0.0,
		'category_case_count': case.category.cases.count() if case.category else 0,
		'original_category_id': original_category.id if original_category else None,
		'original_category_case_count': original_category.cases.count() if original_category else None,
		'original_category_case_cost': original_category.cost() if original_category else None,
		'uncategorized_case_cost': uncategorized_case_detail['cost'],
		'uncategorized_case_count': uncategorized_case_detail['count']
	}

	return json.jsonify(return_obj)

@invoicing.route('/invoice/<invoice_id>', methods=['GET'])
@invoicing.route('/invoice', methods=['GET'])
@login_required
def invoice(invoice_id=None):

	milestones = []
	unpaid_deliverables = []
	refund_deliverables = []

	invoice = None

	if invoice_id:
		invoice = g.db.query(Invoice).get(invoice_id)
		milestones = invoice.milestones.all()
		unpaid_deliverables = g.db.query(Deliverable).filter(Deliverable.invoice==invoice)
		refund_deliverables = g.db.query(Deliverable).filter(Deliverable.invoice!=None, Deliverable.refund_invoice==invoice)
	else:
		milestones = g.db.query(Milestone).filter(Milestone.bfrozen==True, Milestone.invoice==None).order_by(Milestone.ixproject, Milestone.dt)
		unpaid_deliverables = g.db.query(Deliverable).filter(Deliverable.invoice==None)
		refund_deliverables = g.db.query(Deliverable).filter(Deliverable.invoice!=None, Deliverable.refund_invoice==None)

	total = sum([ float(m.billable_cost()) for m in milestones ]) + sum([ d.festimate for d in unpaid_deliverables]) - sum([ d.frefunded for d in refund_deliverables])
	deliverable_total = sum([ d.festimate for d in unpaid_deliverables]) - sum([ d.frefunded for d in refund_deliverables])

	return render_template('invoicing/invoice.html', invoice=invoice, milestones=milestones, unpaid_deliverables=unpaid_deliverables, refund_deliverables=refund_deliverables, total=total, deliverable_total=deliverable_total, print_view=g.print_view)

@invoicing.route('/invoice', methods=['PUT'])
@login_required
def invoice_finalize():
	
	success = False
	message = ""
	result = {}

	try:

		company = g.db.query(Company).first()
		customer = g.db.query(Customer).first()

		invoice_id = None

		if 'invoice_id' in request.form:
			invoice_id = request.form['invoice_id']

		if invoice_id:

			invoice = g.db.query(Invoice).get(invoice_id)
			invoice.state = 'final'

			for m in invoice.milestones:
				m.finvoicedamount = float(m.billable_cost())
				#m.binvoiced = True
				#m.invoice_id = invoice.id

			g.db.commit()

			flash("Invoice #%s finalized" % invoice.id)

		else:

			milestones = g.db.query(Milestone).filter(Milestone.bfrozen==True, Milestone.invoice==None)
			unpaid_deliverables = g.db.query(Deliverable).filter(Deliverable.invoice==None)
			refund_deliverables = g.db.query(Deliverable).filter(Deliverable.invoice!=None, Deliverable.refund_invoice==None)

			if len(list(milestones)) > 0 or len(list(unpaid_deliverables)) > 0 or len(list(refund_deliverables)) > 0:

				invoice = Invoice()				
				invoice.company_id = company.id
				invoice.customer_id = customer.id
				invoice.state = 'final'

				g.db.add(invoice)

				g.db.commit()

				for m in milestones:
					m.finvoicedamount = float(m.billable_cost())
					#m.binvoiced = True
					m.invoice_id = invoice.id

				for d in unpaid_deliverables:
					d.invoice_id = invoice.id

				for d in refund_deliverables:
					d.refund_invoice_id = invoice.id

				g.db.commit()

				flash("Invoice #%s created" % invoice.id)

		success = True

	except:
		logger.error(str(sys.exc_info()[0]))
		message = str(sys.exc_info()[1])
		logger.error(message)
		flash(message)
		traceback.print_tb(sys.exc_info()[2])

	return json.jsonify({'success': success, 'message': message, 'result': result})

@invoicing.route('/invoice/<invoice_id>', methods=['PUT'])
@login_required
def invoice_update(invoice_id):

	action = request.form['action']

	if action == 'revert':

		invoice = g.db.query(Invoice).get(invoice_id)
		
		#for milestone in invoice.milestones:
		#	milestone.binvoiced = False

		invoice.state = 'working'

		g.db.commit()

	return redirect(url_for("invoicing.invoices")), 303

@invoicing.route('/invoices', methods=['GET'])
@login_required
def invoices():
	invoices = g.db.query(Invoice).order_by(Invoice.date_created).all()
	return render_template('invoicing/invoices.html', invoices=invoices)

@invoicing.route('/deliverables', methods=['GET'])
@login_required
def deliverables():

	deliverables = g.db.query(Deliverable).all()

	return render_template('invoicing/deliverables.html', deliverables=deliverables)

@invoicing.route('/deliverable/<deliverable_id>/refund', methods=['PUT'])
@login_required
def deliverable_refund(deliverable_id):

	success = False
	message = ""
	result = {}

	deliverable = g.db.query(Deliverable).get(deliverable_id)

	if deliverable.frefunded == 0:
		deliverable.frefunded = deliverable.balance()		
		g.db.commit()

	success = True

	return json.jsonify({'success': success, 'message': message, 'result': result})

@invoicing.route('/deliverable/', methods=['GET', 'POST'])
@invoicing.route('/deliverable/<deliverable_id>', methods=['GET', 'POST'])
@login_required
def deliverable_form(deliverable_id=None):

	'''
	0a - estimate not invoiced
	0b - estimate assigned to a working invoice
		- any detail may be changed except the assignment of a refund invoice
	1 - estimate assigned to a finalized invoice
		- no detail may be changed
		- remainder may be refunded
		- no case may be assigned
	2a - partially refunded, refund not invoiced
	2b - partially refunded, refund assigned to a working invoice
		- the only change allowed is the unassignment, assignment, or change of the refund invoice
	3 - partially refunded, refund assigned to a finalized invoice
		- no detail may be changed
	'''

	deliverable = None

	if deliverable_id:
		deliverable = g.db.query(Deliverable).get(deliverable_id)

	show_refund_invoices = False

	if deliverable:
		if (deliverable.invoice and deliverable.invoice.state == 'final') \
			or (deliverable.frefunded != 0 and deliverable.refund_invoice and deliverable.refund_invoice.state == 'final'):
			# we cannot change any details
			flash("This deliverable is assigned to a finalized invoice - no changes may be made.")
			return redirect('invoicing.deliverables')
		if deliverable.frefunded != 0 and (not deliverable.refund_invoice or deliverable.refund_invoice.state == 'working'):
			show_refund_invoices = True

	form = DeliverableForm(request.form, deliverable)
	working_invoices = [ (0, "Default Working Invoice") ] + [ (i.id, "%s: %s" %(i.customer.name, i.date_created)) for i in g.db.query(Invoice).filter(Invoice.state=='working') ]
	form.invoice_id.choices = working_invoices
	form.refund_invoice_id.choices = working_invoices

	if form.validate_on_submit():

		if deliverable:
			form.populate_obj(deliverable)
			if deliverable.invoice_id == 0:
				deliverable.invoice_id = None
			if deliverable.refund_invoice_id == 0:
				deliverable.refund_invoice_id = None
		else:
			deliverable = Deliverable(name=form.name.data, festimate=form.festimate.data)
			
			if form.invoice_id.data > 0:
				deliverable.invoice_id = form.invoice_id.data
			if form.refund_invoice_id.data > 0:
				deliverable.refund_invoice_id = form.refund_invoice_id.data

			g.db.add(deliverable)

		g.db.commit()
		
		flash("The deliverable entry was created or updated")
		return redirect(url_for("invoicing.deliverables"))

	elif form.errors:

		flash("The submission was invalid. Please try again.")

	if not show_refund_invoices and deliverable and not deliverable.refund_invoice_id:
		form.refund_invoice_id.data = 0

	return render_template("invoicing/deliverable_form.html", deliverable=deliverable, form=form, show_refund_invoices=show_refund_invoices)

@invoicing.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():

	payment = None
	form = PaymentForm(request.form)

	if form.validate_on_submit():

		form.populate_obj(payment)
		g.db.add(payment)
		g.db.commit()

		flash("The payment has been filed")
		return redirect(url_for('invoicing.invoices'))

	return render_template("invoicing/_payment.html", form=form)

@invoicing.route('/', methods=['GET', 'POST'])
@login_required
def milestones():

	'''
	milestone_filter = None
	person_filter = None
	project_filter = None
	start_milestone = None
	end_milestone = None
	single_milestone = False
	'''

	try:

		#projects = g.db.query(Project).all()
		milestones = g.db.query(Milestone).order_by(Milestone.dt.desc()).all()
		#people = g.db.query(FogbugzUser).all()

		#project_names = {}
		
		#for p in projects:
		#	project_names[p.ixproject.string] = parse_cdata(p.sproject.string)

		
		'''
		if request.method == "POST":
			milestone_filter = request.form['milestone_filter'] if request.form['milestone_filter'] != "" else ""
			person_filter = request.form['person_filter'] if request.form['person_filter'] != "" else None
			project_filter = int(request.form['project_filter']) if request.form['project_filter'] != "" else None
			start_milestone = request.form['start_milestone'] if request.form['start_milestone'] != "" else None
			end_milestone = request.form['end_milestone'] if request.form['end_milestone'] != "" else None
		'''

		#single_milestone = bool(request.form['single_milestone']) if 'single_milestone' in request.form else False

		#fixfors = sorted(fixfors, key=lambda fixfor: fixfor.dt, reverse=True)
		#milestones_filter = sorted(milestones_filter, key=lambda fixfor: fixfor.dt, reverse=True)

		''' filter stuff 

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
		
		if person_filter is not None and int(c.ixpersonresolvedby.string) != int(person_filter):
			continue

		if project_filter is not None and int(c.ixproject.string) != int(project_filter):
			continue

		'''


		'''
		person_names = []
		project_names = []
		return render_template('invoicing/milestones.html', person_names=person_names, project_names=project_names,
							   milestone_filter=milestone_filter,
							   person_filter=person_filter, project_filter=project_filter,
							   start_milestone=start_milestone, end_milestone=end_milestone,
							   single_milestone=single_milestone)#,
							   #description=description)#, fixfors=fixfors, milestones_filter=milestones_filter, total_hours=total_hours, total_cost=total_cost)
		'''

	except:

		print sys.exc_info()
		traceback.print_tb(sys.exc_info()[2])
		return render_template('error.html', error=sys.exc_info()[2])

	return render_template('invoicing/milestones.html', 
		#projects=projects,
		milestones=milestones
		#people=people, 
		#project_names=project_names,
	   	#milestone_filter=milestone_filter,
	   	#person_filter=person_filter, 
	   	#project_filter=project_filter,
	   	#start_milestone=start_milestone, 
	   	#end_milestone=end_milestone,
	   	#single_milestone=single_milestone
	   	#description=description, 
	   	#fixfors=fixfors, 
	   	#milestones_filter=milestones_filter, 
	   	#total_hours=total_hours, 
	   	#total_cost=total_cost
	)


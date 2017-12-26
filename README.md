# Qk Strt

1. Fill out instance/config_[your environment name].py with appropriate information for your Fogbugz account

2. Create .env with

		DATABASE_URL=[database connection string]
		HEADLMP_ENVIRONMENT=[your environment name]
		LOG_LEVEL=[numeric Logging.* (10, 20, 30, 40, 50)]

2. Install pip requirements:

		$ sudo pip install -r requirements.txt

3. Create virtual environment:

		$ source env/bin/activate

3. Run the app

		(env) $ python run.py runserver
	
	`run.py runserver` will emulate `heroku local` (described below) in finding `.env` and loading this into `os.environ`, importing `app` from `/webapp`, creating a `flask.ext.script.Server` and `Manager` instance, and calling `run()` on the Manager instance. This excludes `/instance/config_*/py` configuration influence.
	
	or 
	
		(env) $ heroku local
	
	`heroku local` will:
	* load `.env` and then 
	* run `Procfile`, which 
	* runs `wsgi.py`, which 
	* imports `app` from `/webapp`, which 
	* loads `config_default.py` and then 
	* overrides that with `/instance/config_development.py` (pulling `HEADLMP_ENVIRONMENT` as `development` from `.env`).

# Development Plan

* when a milestone ends, it and its cases are candidates to be loaded from FB into a working space
* a milestone's cases can be categorized, comped, and charged against a paid deliverable
* at any point during the organization of a milestone's cases, the milestone can be frozen
* frozen milestones appear in the Working Invoice
* the Working Invoice is a fluid, working document
* organization of a milestone's cases can continued after the milestone is frozen
* when all milestones intended for an invoice have been organized and frozen, the invoice is ready to create
* when an invoice is created from the Working Invoice, it is no longer editable and is ready to be submitted
* submission is done by viewing the invoice in 'print mode', printing to PDF from the browser, and manually transferring the PDF to the client

## state of development November 4, 2016
* when payment is received, it is entered and applied to one or more invoices
* invoices that are paid in full are marked as 'paid', partially-paid invoices as 'partially-paid'
* if an invoice needs modification, it can be reverted to be a Working Invoice
* reverting an invoice sets state from 'final' to 'working'
* reverting an invoice does not delete the invoice, it only returns it to an editable state
* there are two types of Working Invoice: an invoice with state == 'working' and the "default" invoice i.e. the comprehensive list of all frozen billables (milestones and deliverables) that have not been assigned to an invoice. 
* a 'working' invoice may have milestones added or removed, just like the default invoice
* while an invoice is reverted to be a Working Invoice, the function of freezing an milestone provides the option to select to which Working Invoice it is to be applied. otherwise, a frozen milestone will automatically be assigned to the default (no invoice yet created) Working Invoice

# Development Notes

* This application was originally written for Fogbugz API version 7, however my account has since been upgraded to API version 8, and everything seems to work fine.

# References

### Fogbugz 

http://help.fogcreek.com/8202/xml-api

http://help.fogcreek.com/8447/how-to-get-a-fogbugz-xml-api-token

* Note: manually obtaining a token is not necessary for this application - the 'fogbugz' Python module will manage your token, given a username and password. 

### Flask

http://flask.pocoo.org/docs/0.10/

### Jinja 

http://jinja.pocoo.org/
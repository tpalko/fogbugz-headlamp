from flask import g
from flask.ext.wtf import Form
from wtforms import IntegerField, TextField, TextAreaField, FileField, SelectField, DateField
import logging

logger = logging.getLogger(__name__)
		
class DeliverableForm(Form):
	id = IntegerField('Id')
	name = TextField('Name')
	festimate = TextAreaField('Estimate')
	invoice_id = SelectField('Invoice', coerce=int)
	refund_invoice_id = SelectField('Refund Invoice', coerce=int)
	date_created = DateField('Date')

class PaymentForm(Form):
	id = IntegerField('Id')
	famount = TextField('Amount')
	date_deposited = DateField('Date Deposited')
from flask.ext.wtf import Form
from wtforms import IntegerField, TextField, TextAreaField, FileField
import logging

logger = logging.getLogger(__name__)
		
class DeliverableForm(Form):
	id = IntegerField('Id')
	name = TextField('Name')
	festimate = TextAreaField('Estimate')

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

base = Blueprint('base', __name__, url_prefix='/')

@base.route('/', methods=['GET'])
def home():
	return redirect(url_for('invoicing.milestones'))
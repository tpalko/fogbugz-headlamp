# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

# Import the database object from the main app module
from webapp.database import db_session

# Import module forms
from webapp.mod_auth.forms import LoginForm, RegisterForm

# Import module models (i.e. User)
from webapp.mod_auth.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

# Set the route and accepted methods
@mod_auth.route('/signin/', methods=['GET', 'POST'])
def signin():

    if session['user_id']:
        return redirect(url_for('invoicing.milestones'))
        
    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):

            session['user_id'] = user.id

            flash('Welcome %s' % user.name)

            return redirect(url_for('milestones'))

        flash('Wrong email or password', 'error-message')

    return render_template("auth/signin.html", form=form)

@mod_auth.route('/register/', methods=['GET', 'POST'])
def register():

    form = RegisterForm(request.form)

    if form.validate_on_submit():

        u = User(form.name.data, form.email.data, generate_password_hash(form.password.data))
        db_session.add(u)
        db_session.commit()

        return redirect(url_for('auth.signin'))

    return render_template("auth/register.html", form=form)

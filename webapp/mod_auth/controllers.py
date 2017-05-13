from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, abort
from flask.ext.login import login_user, login_required, current_user, logout_user
from werkzeug import check_password_hash, generate_password_hash
from webapp.mod_auth.forms import LoginForm, RegisterForm
from webapp.mod_auth.models import User, LoginUser
from webapp import logger
import json

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_auth = Blueprint('auth', __name__, url_prefix='/auth')

# Set the route and accepted methods
@mod_auth.route('/signin/', methods=['GET', 'POST'])
def signin():

    logger.debug("auth: %s, active: %s, anon: %s" %(current_user.is_authenticated, current_user.is_active, current_user.is_anonymous))

    if current_user.is_authenticated:
        return redirect(url_for('invoicing.milestones'))
        
    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():

        logger.debug("Looking for user %s " % form.email.data)

        user = g.db.query(User).filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):

            logger.debug("Found user %s: %s" %(user.email, user.name))

            remember = False
            if 'remember' in form:
                remember = True

            logger.debug("Logging in user %s.." % user.name)
            session_user = LoginUser(user.name, user.id, user.is_active)
            login_user(session_user, remember)
            logger.debug("Logged in %s" % user.name)

            flash('Welcome %s' % user.name)

            next = request.args.get('next')

            #if not next_is_valid(next):
            #    return abort(400)

            return redirect(next or url_for('invoicing.milestones'))

        else:
            
            flash('Wrong email or password', 'error-message')

    return render_template("auth/signin.html", form=form)

@mod_auth.route('/register/', methods=['GET', 'POST'])
def register():

    form = RegisterForm(request.form)

    if form.validate_on_submit():

        u = User(form.name.data, form.email.data, generate_password_hash(form.password.data))

        g.db.add(u)
        g.db.commit()

        return redirect(url_for('auth.signin'))

    return render_template("auth/register.html", form=form)

@mod_auth.route('/logout/', methods=['GET'])
@login_required
def logout():

    logout_user()

    return redirect(url_for('auth.signin'))
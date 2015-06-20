# -*- coding: utf-8 -*-

from app import app, db
from flask import redirect, url_for, flash, request, render_template, g, session
from forms import LoginForm, SigninForm
from models import User
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask.ext.babel import gettext
from config import USER_ROLES


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        #session['remember_me'] = form.remember_me.data
        nickname = form.nickname.data
        password = form.password.data
        user = User.query.filter_by(nickname=nickname).first()
        if user is None:
            flash(gettext('Entered username is unknown.'))
            return redirect(url_for('login'))
        if not check_password_hash(user.password, password):
            flash(gettext('Password is incorrect!'), 'error')
            return redirect(url_for('login'))
        login_user(user)
        if 'cart' in session:
            session.pop('cart')
        flash(gettext("Logged in successfully."))
        return redirect(request.args.get("next") or url_for("index"))
    return render_template('login/login.html',
                           title=gettext('Log In'),
                           form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()

    if form.validate_on_submit():

        if len(User.query.filter_by(nickname=form.nickname.data).all()) > 0:
            flash(gettext("Selected username already exists!"))
            return redirect(url_for('signin'))

        new_email = form.email.data
        check_mail = User.query.filter_by(email=new_email).all()

        #user mail already exists
        if len(check_mail) > 0:
            flash(gettext('Selected email is already in use!'))
            return redirect(url_for('signin'))

        user = User()
        user.nickname = form.nickname.data
        user.password = generate_password_hash(form.password.data)
        user.email = new_email
        user.language = form.language.data

        # default role is user, not admin
        user.role = USER_ROLES['ROLE_USER']

        db.session.add(user)
        db.session.commit()

        flash(gettext('Thank you for joining us!'))
        return redirect(url_for('index'))

    return render_template('login/signin.html',
                           title=gettext('Sign In'),
                           form=form)
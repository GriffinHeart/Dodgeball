# -*- coding: utf-8 -*-

from app import app, lm
from flask import render_template
from flask_login import login_required
from flask.ext.babel import gettext
from models import User
from config import LANGUAGES, USER_ROLES


@app.route('/admin/menu')
@login_required
def adminmenu():
    return render_template('/admin/menu.html',
                           title=gettext('Admin Menu'))


@app.route('/admin/usermanagement')
@login_required
def usermanagement():
    users = User.query.all()
    return render_template('/admin/usermanagement.html',
                           title=gettext('User Management'),
                           users=users,
                           LANGUAGES=LANGUAGES,
                           USER_ROLES=USER_ROLES)

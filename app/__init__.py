# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask.ext.babel import Babel
from flask.ext.babel import gettext
from momentjs import momentjs
from googletimeconv import googletimeconv

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = gettext('Please log in to access this page.')

babel = Babel(app)

app.jinja_env.globals['momentjs'] = momentjs
app.jinja_env.globals['googletimeconv'] = googletimeconv

from config import GOOGLE_CALENDAR_API_KEY
from apiclient.discovery import build
calendar_service = build(serviceName='calendar', version='v3', developerKey=GOOGLE_CALENDAR_API_KEY)

from app import viewsBase, viewsLogin, viewsAdmin
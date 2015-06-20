# -*- coding: utf-8 -*-

from app import app, lm, babel, calendar_service
from flask import render_template, request, g, url_for, redirect, flash, session
from flask_login import current_user, login_required
from models import User, Event
from forms import CreateEventForm
from config import LANGUAGES, USER_ROLES, CALENDAR_ID, GOOGLE_API_SCOPES, CLIENT_SECRET_FILE, CALENDAR_CREDENTIALS_DIR
from flask.ext.babel import gettext
from oauth2client import client
from apiclient.discovery import build
from datetime import datetime
import httplib2
import os


@app.before_request
def before_request():
    g.user = current_user
    g.USER_ROLES = USER_ROLES


@app.route('/')
@app.route('/index')
def index():
    now = datetime.utcnow().isoformat() + 'Z'
    calendar = calendar_service.events().list(
        calendarId=CALENDAR_ID, timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = calendar['items']

    return render_template('index.html',
                           events=events)


@app.route('/createevent', methods=['GET', 'POST'])
@login_required
def createevent():

    form = CreateEventForm()

    flow = client.flow_from_clientsecrets(os.path.join(CALENDAR_CREDENTIALS_DIR, CLIENT_SECRET_FILE),
                                          GOOGLE_API_SCOPES,
                                          redirect_uri=url_for('createevent', _external=True))

    if form.validate_on_submit():
        event = Event()
        event.summary = form.summary.data
        event.description = form.description.data
        event.location = form.location.data

        start_dt = datetime.strptime(form.start_dt.data, '%Y-%m-%d %I:%M %p')
        event.start_dt = start_dt

        end_dt = datetime.strptime(form.end_dt.data, '%Y-%m-%d %I:%M %p')
        event.end_dt = end_dt

        session['event_data'] = event

        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)

    code = request.args.get('code')
    if code:

        event = None
        if 'event_data' in session:
            event = session['event_data']
        else:
            flash(gettext('Event data not found!'))

        credentials = flow.step2_exchange(code)
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('calendar', 'v3', http=http)

        start_dt = datetime.strftime(event.start_dt, '%Y-%m-%dT%H:%M:00+09:00')
        end_dt = datetime.strftime(event.end_dt, '%Y-%m-%dT%H:%M:00+09:00')

        event_data = {
            'summary': event.summary,
            'location': event.location,
            'description': event.description,
            'start': {
                'dateTime': start_dt,
                'timeZone': 'Asia/Tokyo',
                },
            'end': {
                'dateTime': end_dt,
                'timeZone': 'Asia/Tokyo',
                }
        }

        new_event = service.events().insert(calendarId=CALENDAR_ID, body=event_data).execute()
        flash(str(new_event.get('htmlLink')))
        return redirect(url_for('index'))

    return render_template('/admin/createevent.html',
                           title=gettext('Create Event'),
                           form=form)


@app.route('/')
@app.route('/user')
@login_required
def user():
    return render_template('user.html')


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@babel.localeselector
def get_locale():
    lang = request.accept_languages.best_match(LANGUAGES.keys())
    if g.user.is_authenticated():
        lang = g.user.language
    return lang
# -*- coding: utf-8 -*-

from app import app, lm, babel, calendar_service, db
from flask import render_template, request, g, url_for, redirect, flash, session
from flask_login import current_user, login_required
from models import User
from forms import EventForm, UserPageForm
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
    form = EventForm()
    session['origin'] = 'createevent'
    if form.validate_on_submit():
        event = set_temp_event_data(form)
        session['event_data'] = event
        return do_event_create()
    elif 'event_data' in session:
        return do_event_create()

    return render_template('/admin/createevent.html',
                           title=gettext('Create Event'),
                           form=form)


@app.route('/editevent', methods=['GET', 'POST'])
@login_required
def editevent():
    form = EventForm()
    session['origin'] = 'editevent'
    if form.validate_on_submit():
        event = set_temp_event_data(form)
        session['event_data'] = event
        return do_event_edit()
    elif 'event_data' in session:
        return do_event_edit()

    event_id = request.args.get('event_id')
    if not event_id:
        flash(gettext('Unknown event id!'), category='alert-danger')
        return redirect(url_for('index'))

    event = calendar_service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
    form = fill_form_with_event_data(form, event)

    return render_template('/admin/editevent.html',
                           title=gettext('Edit Event'),
                           form=form)


@app.route('/deleteevent', methods=['GET', 'POST'])
@login_required
def deleteevent():
    event_id = request.args.get('event_id')
    if not event_id:
        if 'event_id_to_del' not in session:
            flash(gettext('Unknown event id!'), category='alert-danger')
            return redirect(url_for('index'))
    else:
        session['event_id_to_del'] = event_id

    session['origin'] = 'deleteevent'
    if 'credentials' not in session:
        return redirect(url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        service = build('calendar', 'v3', http=http_auth)
    if 'event_id_to_del' in session:
        event_id = session.pop('event_id_to_del', None)
    else:
        flash(gettext('There was some problem with the request. The event was not deleted.'), category='alert-danger')
    service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
    flash(gettext('Event was succesfully deleted.'))

    return redirect(url_for('index'))


def do_event_create():
    event_data = get_event_data_from_session()
    if 'credentials' not in session:
        return redirect(url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        service = build('calendar', 'v3', http=http_auth)
    new_event = service.events().insert(calendarId=CALENDAR_ID, body=event_data).execute()

    session.pop('event_data', None)
    if new_event:
        flash(gettext('Event was succesfully created.'))
    else:
        flash(gettext('There was some problem with the request. The event was not created.'), category='alert-danger')

    return redirect(url_for('index'))


def do_event_edit():
    event_data = get_event_data_from_session()
    if 'credentials' not in session:
        return redirect(url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(session['credentials'])
    if credentials.access_token_expired:
        return redirect(url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        service = build('calendar', 'v3', http=http_auth)
    updated_event = service.events().update(calendarId=CALENDAR_ID, eventId=event_data['id'], body=event_data).execute()

    session.pop('event_data', None)
    if updated_event:
        flash(gettext('Event was succesfully updated.'))
    else:
        flash(gettext('There was some problem with the request. The event was not updated.'), category='alert-danger')

    return redirect(url_for('index'))


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        os.path.join(CALENDAR_CREDENTIALS_DIR, CLIENT_SECRET_FILE),
        scope=GOOGLE_API_SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True))
    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials'] = credentials.to_json()
        origin = 'index'
        if 'origin' in session:
            origin = session.pop('origin', None)
        return redirect(url_for(origin))


@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
    form = UserPageForm()
    if form.validate_on_submit():
        user = current_user
        user.language = form.language.data
        db.session.add(user)
        db.session.commit()
        flash(gettext('Your preferences have been saved.'))
        return redirect(url_for('user'))
    return render_template('user.html',
                           title=gettext('User Page'),
                           form=form,
                           LANGUAGES=LANGUAGES)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@babel.localeselector
def get_locale():
    lang = request.accept_languages.best_match(LANGUAGES.keys())
    if g.user.is_authenticated():
        lang = g.user.language
    return lang


def get_event_data_from_session():
    if 'event_data' in session:
        event_data = session['event_data']
        return event_data
    else:
        flash(gettext('Event data not found!'), category='alert-danger')
        return redirect(url_for('index'))


def set_temp_event_data(form):
    start_dt = datetime.strftime(datetime.strptime(form.start_dt.data, '%Y-%m-%d %I:%M %p'), '%Y-%m-%dT%H:%M:00+09:00')
    end_dt = datetime.strftime(datetime.strptime(form.end_dt.data, '%Y-%m-%d %I:%M %p'), '%Y-%m-%dT%H:%M:00+09:00')
    return {
        'id': form.google_id.data,
        'summary': form.summary.data,
        'location': form.location.data,
        'description': form.description.data,
        'start': {
            'dateTime': start_dt,
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': end_dt,
            'timeZone': 'Asia/Tokyo',
        }
    }


def fill_form_with_event_data(form, event):
    form.summary.data = event.get('summary')
    form.description.data = event.get('description')
    form.location.data = event.get('location')
    if event.get('start').get('dateTime'):
        form.start_dt.data = datetime.strftime(datetime.strptime(event.get('start').get('dateTime'),
                                                                 '%Y-%m-%dT%H:%M:00+09:00'), '%Y-%m-%d %I:%M %p')
    if event.get('end').get('dateTime'):
        form.end_dt.data = datetime.strftime(datetime.strptime(event.get('end').get('dateTime'),
                                                                 '%Y-%m-%dT%H:%M:00+09:00'), '%Y-%m-%d %I:%M %p')
    form.google_id.data = event.get('id')
    return form
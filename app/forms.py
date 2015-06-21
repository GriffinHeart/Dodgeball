# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, HiddenField
from wtforms.fields.html5 import EmailField
from wtforms import validators
from flask.ext.babel import lazy_gettext
from config import LANGUAGES


class LoginForm(Form):
    nickname = StringField(lazy_gettext('Nickname'), [validators.data_required()])
    password = PasswordField(lazy_gettext('Password'), [validators.data_required(),
                                          validators.length(min=5, max=30)])
    submit = SubmitField(lazy_gettext('Submit'))


class SigninForm(Form):
    nickname = StringField(lazy_gettext('Nickname'), [validators.data_required(),
                                                      validators.length(min=5, max=30)])
    password = PasswordField(lazy_gettext('Password'), [validators.data_required(),
                                          validators.length(min=5, max=30)])
    password_confirm = PasswordField(lazy_gettext('Password confirmation'),
                                     [validators.data_required(),
                                      validators.length(min=5, max=30),
                                      validators.equal_to('password',
                                                          message=lazy_gettext('New password must match confirmation!'))])
    email = EmailField(lazy_gettext('Email'), [validators.data_required(),
                                               validators.length(max=120)])
    inv_lang = dict((v, k) for k, v in LANGUAGES.items())
    lang = [(v, k) for k, v in inv_lang.iteritems()]
    language = SelectField(lazy_gettext('Preferred language'), choices=lang)
    submit = SubmitField(lazy_gettext('Submit'))


class EventForm(Form):
    summary = StringField(lazy_gettext('Summary'), [validators.data_required(),
                                                    validators.length(max=300)])
    description = TextAreaField(lazy_gettext('Description'), [validators.length(max=1000)])
    location = StringField(lazy_gettext('Location'), [validators.length(max=300)])
    start_dt = StringField(lazy_gettext('Start Date and Time'))
    end_dt = StringField(lazy_gettext('End Date and Time'))
    google_id = HiddenField()
    submit = SubmitField(lazy_gettext('Submit'))


class UserPageForm(Form):
    inv_lang = dict((v, k) for k, v in LANGUAGES.items())
    lang = [(v, k) for k, v in inv_lang.iteritems()]
    language = SelectField(lazy_gettext('Preferred language'), choices=lang)
    submit = SubmitField(lazy_gettext('Submit'))
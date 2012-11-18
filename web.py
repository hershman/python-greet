from flask import Flask, render_template, redirect, request, url_for
from werkzeug import ImmutableDict, generate_password_hash, check_password_hash
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from wtforms import Form, BooleanField, TextField, PasswordField, validators
import string
from random import choice
from datetime import datetime

#enable hamlish-jinja!!! https://github.com/Pitmairen/hamlish-jinja
class FlaskWithHamlish(Flask):
    jinja_options = ImmutableDict(extensions=['jinja2.ext.autoescape', 'jinja2.ext.with_', 'hamlish_jinja.HamlishExtension'])



app = FlaskWithHamlish(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.jinja_env.hamlish_mode = 'indented' # if you want to set hamlish settings
db = SQLAlchemy(app)

engine = create_engine('sqlite:////tmp/test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
    autoflush=False,
    bind=engine))

#debug/log settings
app.debug = True
if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler(LOG_FN)
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)


##########Users
# Standard Databases
class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    pwdhash = db.Column(db.String())
    email = db.Column(db.String(60))
    activate = db.Column(db.Boolean)
    created = db.Column(db.DateTime)

    def __init__(self, name, email, password=None):
        self.name = name
        if password:
            self.pwdhash = generate_password_hash(password)
        else:
            print "CHECK FOR EMAIL!!!!"
            random_password = self.GenPasswd2()
            print "Made account for %s with PW=%s.  Impliment emailing this!!!! See http://packages.python.org/flask-mail/" % (self.name, random_password)
            self.pwdhash = generate_password_hash(random_password)
        self.email = email
        self.activate = False
        self.created = datetime.utcnow()

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def GenPasswd2(self, pw_length=12, chars=string.letters + string.digits):
        return ''.join([choice(chars) for i in range(pw_length)])

class Event(db.Model):
    __tablename__ = 'events'
    hashtag = db.Column(db.String(60), primary_key=True)
    name = db.Column(db.String(60))
    created = db.Column(db.DateTime)

    def __init__(self, hashtag, name):
        self.name = name
        self.hashtag = hashtag
        self.created = datetime.utcnow()

    def __str__(self):
        return self.name

class EventUser(db.Model):
    __tablename__ = 'event_users'
    uid = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.ForeignKey("events.hashtag"))
    user_id = db.Column(db.ForeignKey("users.uid"))
    image= db.Column(db.String(60))
    tag1 = db.Column(db.String(120))
    tag2 = db.Column(db.String(120))
    tag3 = db.Column(db.String(120))
    created = db.Column(db.DateTime)

    def __init__(self, event_id, user_id, image, tag1, tag2, tag3):
        #check that event_id, user_id not in events.
        self.event_id = event_id
        self.user_id = user_id
        self.image = image
        self.tag1 = tag1
        self.tag2 = tag2
        self.tag3 = tag3
        self.created = datetime.utcnow()

    def __str__(self):
        return self.name

class Tag(db.Model):


# Standard Forms
class signup_form(Form):
    name = TextField('Name', [validators.Required()])
    email = TextField('email', [validators.Required()]) ###TODO: ADD EMAIL VALIDATOR

class login_form(Form):
    username = TextField('Username', [validators.Required()])
    password = TextField('Password', [validators.Required()])

class event_search_form(Form):
    name = TextField('Name', [validators.Required()])

class event_new_form(Form):
    hashtag = TextField('Hashtag', [validators.Required()])
    name = TextField('Name', [validators.Required()])

class event_join_form(Form):
    image = TextField('Image', [validators.Required()])
    tag1 = TextField('Tag1', [validators.Required()])
    tag2 = TextField('Tag2', [validators.Required()])
    tag3 = TextField('Tag3', [validators.Required()])

@app.route("/")
def Index():
    return render_template("index.haml")

@app.route('/user/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = signup_form(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.name.data, form.email.data)
        print "adding user"
        db_session.add(user)
        return redirect(url_for('enter_eventid'))
    return render_template('sign_up.haml', form=form)


@app.route("/user/log_in")
def log_in():
    return render_template("user/log_in.haml")

@app.route("/event/enterid/", methods=['GET', 'POST'])
def enter_eventid():
    form = event_search_form(request.form)
    if request.method == 'POST' and form.validate():
        event_id = form.name.data
        return redirect(url_for('event_join', event_id = event_id))
    return render_template("event/enter_id.haml", form=form)


@app.route('/event/new/', methods=['GET', 'POST'])
def new_event():
    form = event_new_form(request.form)
    if request.method == 'POST' and form.validate():
        event = Event(form.hashtag.data, form.name.data)
        db_session.add(event)
        return redirect(url_for('event_join', event_id = form.hashtag.data))
    return render_template('event/new.haml', form=form)

#REQUIRELOGIN!!!!
@app.route('/event/join/<string:event_id>/', methods=['GET', 'POST'])
def event_join(event_id):
    form = event_join_form(request.form)
    if request.method == 'POST' and form.validate():
        event = Event(form.hashtag.data, form.name.data)
        db_session.add(event)
        return redirect(url_for('event_join', event_id = form.hashtag.data))
    return render_template('event/join.haml', form=form, hashtag=event_id)

if __name__ == "__main__":
    db.create_all()
    app.run()

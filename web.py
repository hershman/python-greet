from flask import Flask, render_template
from werkzeug import ImmutableDict, generate_password_hash, check_password_hash
from flask.ext.sqlalchemy import SQLAlchemy

#enable hamlish-jinja!!! https://github.com/Pitmairen/hamlish-jinja
class FlaskWithHamlish(Flask):
    jinja_options = ImmutableDict(extensions=['jinja2.ext.autoescape', 'jinja2.ext.with_', 'hamlish_jinja.HamlishExtension'])



app = FlaskWithHamlish(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.jinja_env.hamlish_mode = 'indented' # if you want to set hamlish settings
db = SQLAlchemy(app)
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
    username = db.Column(db.String(60))
    pwdhash = db.Column(db.String())
    email = db.Column(db.String(60))
    activate = db.Column(db.Boolean)
    created = db.Column(db.DateTime)

    def __init__(self, username, email, password=None):
        self.username = username
        if password:
            self.pwdhash = generate_password_hash(password)
        else:
            #make random password
            self.pwdhash = generate_password_hash(random_password)
            #send email with the info!!!!!
        self.email = email
        self.activate = False
        self.created = datetime.utcnow()

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

# Standard Forms
class signup_form(Form):
    username = TextField('Username', [validators.Required()])
    email = TextField('email', [validators.Required()])

class login_form(Form):
    username = TextField('Username', [validators.Required()])
    password = TextField('Password', [validators.Required()])


@app.route("/")
def Index():
    return render_template("index.haml")
@app.route("/user/sign_up/")
def sign_up():
    return render_template("user/sign_up.haml", form=signup_form)
@app.route("/user/log_in")
def log_in():
    return render_template("user/log_in.haml")


if __name__ == "__main__":
    db.create_all()
    app.run()

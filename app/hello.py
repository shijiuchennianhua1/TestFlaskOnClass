from flask import Flask, make_response, abort, render_template, url_for, session, redirect
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from app.main.form import NameForm
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate
from flask_mail import Mail, Message
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = '*^*9595∑åß∂'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://chenxuan:zhimakaimen@127.0.0.1/pblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = '3157684388@qq.com'
app.config['MAIL_PASSWORD'] = 'inbrawhtarefdgjg'
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASK_MAIL_SENDER'] = 'FLASKY Admin <3157684388@qq.com>'
app.config['FLASK_ADMIN'] = '3157684388@qq.com'


db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject
                  , sender=app.config['FLASK_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    user = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    response = make_response('<h1>This document carries a cookie!</h1>') 
    response.set_cookie('answer', '42')
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data, role=Role.query.filter_by(name='user').first())
            db.session.add(user)
            db.session.commit()
            # 表明是新注册的用户
            session['know'] = False
            if app.config['FLASK_ADMIN']:
                send_email(app.config['FLASK_ADMIN'], 'New User', 'mail/new_user', user=user.username)
        else:
            session['know'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', content='sadadas', current_time=datetime.utcnow(), form=form,
                           name=session.get('name'), know=session.get('know', False))


@app.route('/user/<string:username>')
def user(username):
    return render_template('user.html', name=username)


@app.route('/user1/<id>')
def user1(id):
    user = None
    if not user:
        print(123)
        abort(404)
    return 'User:{}'.format(id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.shell_context_processor 
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


if __name__ == "__main__":
    app.run(debug=1, port=5000)

from flask import Flask, request, make_response, abort, render_template, url_for, session, redirect, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from form import NameForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = '*^*9595∑åß∂'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://chenxuan:zhimakaimen@127.0.0.1/pblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/', methods=['POST','GET'])
@app.route('/index', methods=['POST','GET'])
def index():
    response = make_response('<h1>This document carries a cookie!</h1>') 
    response.set_cookie('answer', '42')
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', content='sadadas', current_time=datetime.utcnow(), form=form, name=session.get('name'))

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

if __name__ == "__main__":
    app.run(debug=1, port=5000)

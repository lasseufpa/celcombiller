import flask
from flask import render_template
from apiConfig_ixfh import db, app, login_manager
from models_ixfh import CDR, User, Admin
from flask import Flask,session, request, flash, url_for, redirect, render_template, abort ,g
from flask.ext.login import login_user , logout_user , current_user , login_required

@app.route('/login', methods=['GET','POST'])
def login_screen():
    if request.method == 'GET':
        return render_template('login.html')


@app.route('/login.php', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    registered_user = Admin.query.filter_by(username=username,password=password).first()
    if registered_user is None:
        flash('Username or Password is invalid' , 'error') 
        # NOTE: flash not working
        return redirect(url_for('ERRO.html'))
    login_user(registered_user)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(id_):
    return Admin.query.get(int(id_))

@app.route('/')
def index():
    """
    Index page, just show the logged username
    """
    return render_template('index.html')

# Create the Flask-Restless API manager.
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Admin, methods=['GET', 'POST', 'DELETE'])
manager.create_api(User, methods=['GET', 'POST', 'DELETE'])
manager.create_api(CDR, methods=['GET', 'DELETE'])

# start the flask loop
app.run()
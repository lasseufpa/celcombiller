import flask
from flask import render_template
from apiConfig_ixfh import db, app, login_manager
from models_ixfh import CDR, User
from flask_restless import ProcessingException
from flask import Flask,session, request, flash, url_for, redirect, render_template, abort ,g
from flask.ext.login import login_user , logout_user , current_user , login_required

@app.route('/login', methods=['GET'])
def login_screen():
    if request.method == 'GET':
        return render_template('login.html')


@app.route('/login.php', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username,password=password).first()
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        return render_template('ERROR.html')
    login_user(registered_user)
    return render_template('loginsuc.html')

@app.route('/logout')
def logout():
    logout_user()
    return render_template('logout.html')

@login_manager.user_loader
def load_user(id_):
    return User.query.get(int(id_))

@app.route('/')
def index():
    """
    Index page, just show the logged username
    """
    return render_template('index.html')

@app.route('/check')
@login_required
def check_login():
    """
    Index page, just show the logged username
    """
    return render_template('check.html')

def auth(*args, **kargs):
    """
    Require API request to be authenticated
    """
    if not current_user.is_authenticated():
        raise ProcessingException(description='Not authenticated', code=401)

def preprocessor_check_adm(search_params, *args, **kargs):
    """
    ok
    """
    if current_user.is_admin():
        pass
    else:
        try:
            filters = search_params['filters']
            if not isinstance(filters, list):
                filters = search_params['filters'] = [filters]
        except KeyError:
            filters = search_params['filters'] = []
        filters.append({
            "name": 'id_',
            "op":"==",
            "val": current_user.get_id(),
        })

def preprocessor_another_route(*args, **kargs):
    """
    print
    """
    if current_user.is_admin():
        pass
    else:
        raise ProcessingException(description='Not authenticated', code=401)

manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create the Flask-Restless API manager.
# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.

manager.create_api(User,
                                preprocessors={
                                  'GET_MANY': [auth, preprocessor_check_adm],
                                  'GET_SINGLE': [auth, preprocessor_another_route],
                                  'PATCH_SINGLE': [auth],
                                  'DELETE_SINGLE': [auth],
                                  'PATCH_MANY': [auth],
                                  'DELETE_MANY': [auth],
                                  },
                                  # methods=['POST', 'PATCH', 'GET'],
                                  primary_key='username'
                                )
                              # methods=['GET', 'POST', 'DELETE'], results_per_page=1)
manager.create_api(CDR, methods=['GET', 'DELETE'])
# manager.create_api(Admin, methods=['GET', 'POST', 'DELETE'])

# start the flask loop
app.run('0.0.0.0', 8080)
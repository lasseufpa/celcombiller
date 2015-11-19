import flask
from flask import Flask, session, request, flash, url_for, redirect, \
    render_template, abort
from apiConfig import db, app, login_manager
from models import CDR, User, CreditsRegister
from time import strftime
from datetime import *
from dateutil.relativedelta import *
from flask_restless import ProcessingException
from flask.ext.login import login_user , logout_user , current_user ,\
    login_required
import json

from openbts import to_openbts

@app.route('/')
def index():
    """
    Index page, just show the logged username
    """
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        registered_user = \
            User.query.filter_by(username=username, password=password).first()
        if registered_user is None:
            flash('Username or Password is invalid', 'error')
            return render_template('ERROR.html')
        login_user(registered_user)
        json_with_names = check_time()
        return render_template('loginsuc.html', json=json_with_names)

def check_time():
    if not current_user.is_admin():
        return False
    else:
        json_need_update = []
        groups = CreditsRegister.query.all()
        for group in groups:
            boolean_time = (group.date_to_update - datetime.now())\
                .total_seconds()
            boolean_time = 1 if boolean_time < 0 else 0
            if boolean_time == 1:
                json_need_update.append(group.name)
        if json_need_update == []:
            return None
        else:
            return json_need_update


def already_has_group(*args, **kargs):
    data = request.data
    request_body = json.loads(data)
    Table_CreditsRegister = CreditsRegister.query.\
        filter_by(name=request_body['name']).first()
    if Table_CreditsRegister is not None:
        raise ProcessingException(description='Already has this Group', code=400)
    else:
        pass

def add_users_to_group(*args, **kargs):
    data = request.data
    request_body = json.loads(data)
    Table_CreditsRegister = CreditsRegister.query.\
        filter_by(name=request_body['name']).first()
    all_users = User.query.all()
    for aux in all_users:
        Table_CreditsRegister.tunel.append(aux)
    db.session.add(Table_CreditsRegister)
    db.session.commit()
    pass

def transform_to_utc(*args, **kargs):
    data = request.data
    request_body = json.loads(data)
    min_day = int(datetime.now().strftime("%d"))
    min_month = int(datetime.now().strftime("%m"))
    min_year = int(datetime.now().strftime("%Y"))
    day = int(request_body['day'])
    year = int(request_body['year'])
    month = int(request_body['month'])
    if year < min_year or ((month < min_month) and (year <= min_year)) or \
        (day < min_day and (month <= min_month and year <= min_year)):
        raise ProcessingException(description='Date not accept', code=400)
    else:
        del kargs['data']['day']
        del kargs['data']['month']
        del kargs['data']['year']
        kargs['data']['date_to_update'] = \
            str(month) + " " + str(day) + " " + str(year) + " 0:0:0 "
        pass

@app.route('/logout')
def logout():
    logout_user()
    return render_template('logout.html')


@login_manager.user_loader
def load_user(id_):
    return User.query.get(int(id_))


@app.route('/check')
@login_required
def check_login():
    """
    Index page, just show the logged username
    """
    return render_template('check.html')


def auth(*args, **kargs):
    """
    Required API request to be authenticated
    """
    if not current_user.is_authenticated():
        raise ProcessingException(description='Not authenticated', code=401)


def preprocessor_check_adm(*args, **kargs):
    if not current_user.is_admin():
        raise ProcessingException(description='Forbidden', code=403)


def preprocessors_patch(instance_id=None, data=None, **kargs):
    user_cant_change = ["admin", "balance", "clid", "id_",
                        "originated_calls", "received_calls, tunel"]
    admin_cant_change = ["id_", "originated_calls", "received_calls"]
    if current_user.is_admin():
        for x in data.keys():
            if x in admin_cant_change:
                raise ProcessingException(description='Forbidden', code=403)
    elif current_user.username == instance_id:
        for x in data.keys():
            if x in user_cant_change:
                raise ProcessingException(description='Forbidden', code=403)
    else:
        raise ProcessingException(description='Forbidden', code=403)


def preprocessors_check_adm_or_normal_user(instance_id=None, **kargs):
    if not (current_user.is_admin() or current_user.username == instance_id):
        raise ProcessingException(description='Forbidden', code=403)

manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create the Flask-Restless API manager.
# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.

manager.create_api(
    User,
    preprocessors={
        'POST': [auth, preprocessor_check_adm],
        'GET_MANY': [auth, preprocessor_check_adm],
        'GET_SINGLE': [auth, preprocessors_check_adm_or_normal_user],
        'PATCH_SINGLE': [
            auth,
            preprocessors_check_adm_or_normal_user,
            preprocessors_patch
        ],
        'PATCH_MANY': [auth, preprocessor_check_adm],
        'DELETE_SINGLE': [auth, preprocessor_check_adm],
    },
	postprocessors={
		'POST':[to_openbts]
	},
    methods=['POST', 'GET', 'PATCH', 'DELETE'],
    allow_patch_many=True,
    primary_key='username')

manager.create_api(
    CDR,
    preprocessors={
        'GET_MANY': [auth, preprocessor_check_adm],
        'GET_SINGLE': [auth, preprocessors_check_adm_or_normal_user],
        'PATCH_SINGLE': [auth, preprocessors_patch],
        'DELETE_SINGLE': [auth, preprocessor_check_adm],
    },
    methods=['GET','PATCH', 'DELETE'])

manager.create_api(
    CreditsRegister,
    preprocessors={
        'POST': [
            auth,
            preprocessor_check_adm,
            already_has_group, transform_to_utc
        ],
        'GET_MANY': [auth, preprocessor_check_adm],
        'GET_SINGLE': [auth, preprocessor_check_adm],
        'PATCH_SINGLE': [auth, preprocessor_check_adm, transform_to_utc],
        'DELETE_SINGLE': [auth, preprocessor_check_adm],
    },
    postprocessors={
        'POST': [add_users_to_group],
    },
    methods=['POST', 'GET', 'PATCH', 'DELETE'],
    primary_key='name')

# start the flask loop
app.debug = True
app.run('0.0.0.0', 5000)

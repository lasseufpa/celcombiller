from flask import Flask,session, request, flash, url_for, redirect, render_template, abort
from apiConfig import db, app, login_manager
from models import CDR, User
from flask_restless import ProcessingException
from flask.ext.login import login_user , logout_user , current_user , login_required

@app.route('/')
def index():
    """
    Index page, just show the logged username
    """
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
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
    if current_user.is_admin():
        pass
    else:
        raise ProcessingException(description='Not authenticated', code=401)

def preprocessors_patch(instance_id=None, data=None, **kargs):
    user_cant_change = [ "admin", "balance", "clid", "id_", "originated_calls", "received_calls" ]
    admin_cant_change = [ "id_", "originated_calls", "received_calls" ]
    if current_user.is_admin():
        for x in data.keys():
            if x in admin_cant_change:
                raise ProcessingException(description='Forbidden', code=403)
    else:
        if current_user.name_is() == instance_id:
            for x in data.keys():
                if x in user_cant_change:
                    raise ProcessingException(description='Forbidden', code=403)

def preprocessors_delete(instance_id=None, **kargs):
    if current_user.is_admin():
        pass
    else:
        if current_user.name_is() == instance_id:
            pass
        else:
            raise ProcessingException(description='Forbidden', code=403)

manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create the Flask-Restless API manager.
# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.

manager.create_api(User,
                        preprocessors={
                            'POST': [auth, preprocessor_check_adm],
                            'GET_MANY': [auth, preprocessor_check_adm],
                            'GET_SINGLE': [auth, preprocessor_another_route],
                            'PATCH_SINGLE': [auth, preprocessors_patch],
                            'DELETE_SINGLE': [auth, preprocessors_delete],
                            # 'PATCH_MANY': [auth, patch_many_preprocessor],
                            # 'DELETE_MANY': [auth],
                        },
                            methods=['POST', 'GET', 'PATCH', 'DELETE'],
                            primary_key='username'
                            )
manager.create_api(CDR, methods=['GET', 'DELETE'])

# start the flask loop
app.debug=True
app.run('0.0.0.0', 8080)
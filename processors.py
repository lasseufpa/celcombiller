import json
import socket;
from flask import request, abort
from models import User

def auth(*args, **kargs):
    """
    Required API request to be authenticated
    """
    # if not current_user.is_authenticated():
    #    raise ProcessingException(description='Not authenticated', code=401)
    pass


def preprocessor_check_adm(*args, **kargs):
   # if not current_user.is_admin():
   #     raise ProcessingException(description='Forbidden', code=403)
    pass


def preprocessors_patch(instance_id=None, data=None, **kargs):
    user_cant_change = ["level", "clid", "_id",
                        "originated_calls", "received_calls"]
    admin_cant_change = ["_id", "originated_calls", "received_calls"]
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

def new_user(*args, **kargs):

    #check if we have connection with nodemanager
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if sock.connect_ex(('127.0.0.1',45064)):
       abort(500) 

    data = request.data
    request_body = json.loads(data)
    username = request_body['username']
    password = request_body['password']
    cpf = request_body['cpf']
    clid = request_body['clid']
    imsi = request_body['imsi']

    if username is None or password is None:
        abort(409)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(409)  # existing user
    if User.query.filter_by(cpf=cpf).first() is not None:
        abort(409)  # existing user
    if User.query.filter_by(clid=clid).first() is not None:
        abort(409)  # existing user
    if User.query.filter_by(imsi=imsi).first() is not None:
        abort(409)  # existing user

    # user = User(username = username)
    # user.hash_password(password)
    # db.session.add(user)
    # db.session.commit()
    # return jsonify({ 'username': user.username }), 201, {'Location':
    # url_for('get_user', id = user.id, _external = True)}
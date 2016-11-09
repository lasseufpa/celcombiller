import zmq
import json
import envoy
import socket as socket_pk
from flask import abort, make_response, jsonify
from .config import NODE_MANAGER_ADDRESS, NODE_MANAGER_PORT
from .models import User


def check_node_manager_connection():
    """check if we have connection with nodemanager"""
    socket = socket_pk.socket(socket_pk.AF_INET, socket_pk.SOCK_STREAM)
    if socket.connect_ex((NODE_MANAGER_ADDRESS, int(NODE_MANAGER_PORT))):
        abort(make_response(jsonify(message="No connection with NodeManager"), 500))
        return False
    else:
        return True


def send_to_openbts(content):
    """ send a request to openbts """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://" + NODE_MANAGER_ADDRESS + ':' + NODE_MANAGER_PORT)
    socket.send_string(json.dumps(content), encoding='utf-8')

    # socket.send_string(json.dumps(create_request), encoding='utf-8')
    # set timeout to send
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    if poller.poll(1000):  # 1s timeout in milliseconds
        msg = socket.recv_json()
    else:
        # TODO: what do we do when the request fail ?
        # raise IOError("Request to OpenBTS Timeout")
        socket.close(linger=1)
        context.term()
        abort(make_response(jsonify(message="No connection with NodeManager"), 500))

    socket.close(linger=1)
    context.term()


def delet_by_imsi(imsi):
    """ delet a openbts user  by imsi"""
    delete_request = {
        'command': 'subscribers',
        'action': 'delete',
        'match': {
            'imsi': 'IMSI' + imsi_old,
        }
    }

    send_to_openbts(delete_request)


def new_user_openbts(result=None, **kw):
    """ create a new user in the openbts, it first delets any user that have the
    that have the same imsi in the openbts database """
    _id = str(result['id'])
    clid = str(result['clid'])
    imsi = str(result['imsi'])

    delet_by_imsi(imsi)

    request = {
        'command': 'subscribers',
        'action': 'create',
        'fields': {
            'name': id,
            'imsi': 'IMSI' + imsi,
                    'msisdn': clid,
                    'ki': ''
        }
    }

    send_to_openbts(request)


def patch_user_openbts(instance_id=None, data=None, **kw):
    """Fist I get the data to be modified then  delete the current information
    in the openbts database and finally I recreate the entrance in the OpenBTS
    database"""

    user = User.query.filter_by(username=instance_id).first()

    id = str(user.id)
    if 'clid' not in data and 'imsi' not in data:
        return

    if 'clid' in data:
        clid = data['clid']
    else:
        clid = user.clid

    if 'imsi' in data:
        imsi_new = data['imsi']
        imsi_old = user.imsi
    else:
        imsi_new = user.imsi
        imsi_old = user.imsi

    delet_by_imsi(imsi)

    create_request = {
        'command': 'subscribers',
        'action': 'create',
        'fields': {
            'name': id,
            'imsi': 'IMSI' + imsi_new,
                    'msisdn': clid,
                    'ki': ''
        }
    }

    send_to_openbts(create_request)


def send_sms(from_clid, to_clid, msg):
    """ send a sms using the openbts executable, it only works if the back-end
    and the openbts are in the same machine """
    # check_node_manager_connection()
    to_imsi = User.query.filter_by(clid=to_clid).first().imsi

    response = envoy.run('/OpenBTS/OpenBTSCLI -c "sendsms ' + str(to_imsi) +
                         ' ' + str(from_clid) + ' ' + msg + '"', timeout=1000)

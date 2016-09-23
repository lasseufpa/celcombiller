import zmq
import json
from config import node_manager_address, node_manager_port
from flask import abort


def new_user_openbts(result=None, **kw):

    _id = str(result["_id"])
    clid = str(result["clid"])
    imsi = str(result["imsi"])

    request = {
        "command": "subscribers",
        "action": "create",
        "fields": {
            "name": _id,
            "imsi": "IMSI" + imsi,
                    "msisdn": clid,
                    "ki": ""
        }
    }

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+node_manager_address+':'+node_manager_port)
    socket.send_string(json.dumps(request), encoding='utf-8')

    # set timeout
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    if poller.poll(1000):  # 1s timeout in milliseconds
        msg = socket.recv_json()
    else:
        # TODO: what do we do when the request fail ?
        # raise IOError("Request to OpenBTS Timeout")
        socket.close(linger=1)
        context.term()
        abort(500, "Conexao com o NodeManager Falhou")


def patch_user_openbts(result=None, **kw):
    print result

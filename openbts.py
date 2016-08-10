import zmq
import json
from flask import abort


def to_openbts(result=None, **kw):

    # for key, value in result.items():
    #     if key == "_id":
    #         _id = value

    #     elif key == "clid":
    #         clid = value

    #     elif key == "imsi":
    #         imsi = value

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
    socket.connect("tcp://127.0.0.1:45064")
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
        abort(500)

import sys
import zmq


def to_openbts(result = None, **kw):

	id_ = ""
	clid = ""
	imsi = ""

	for key,value  in result.items():
		if key == "id_":
			id_ = value

		elif key == "clid":
			clid = value

		elif key == "imsi":
			imsi = value

	request = '{"command":"subscribers","action":"create","fields":{"name":"' + str(id_) + '","imsi":"IMSI' + str(imsi) + '","msisdn":"' + str(clid) + '","ki":""}}'


	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("tcp://127.0.0.1:45064")

	socket.send(request)



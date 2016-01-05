#!/usr/bin/env python
"""
celcombiller AGI:
    * Consult the user balance and authorize a call
    * Save the call CDRs
    * Update the user balance
"""
# pylint: disable=C0103
from datetime import datetime
import asterisk.agi
#from asterisk.agi import AGIAppError
from models import User

import requests
import json

adm_user = 'admin'
adm_pssw = 'adm123'

agi = asterisk.agi.AGI()


from_user = User.query.filter_by(
    clid=agi.env['agi_callerid']).first()
to_user = User.query.filter_by(
    clid=agi.get_variable('CDR(B-Number)')).first()

if agi.get_variable('DIALSTATUS') == 'ANSWER':
    # Time from answer to hangup
    billsec = int(agi.get_variable('CDR(billsec)'))
    # Time the user answered
    answer = datetime.fromtimestamp(float(agi.get_variable('CDR(answer,u)')))

    # Create a session
    s = requests.Session()
    # Login the session
    s.post('http://localhost:5000/login',\
            data={'username':adm_user, 'password': adm_pssw})

    # Create a new CDR record
    payload = '{"answer":"'+ str(answer)+'", "billsec":"'+ \
            str(billsec)+'", "from_user_id": '+\
            str(from_user.id_)+', "to_user_id":'+ str(to_user.id_)+'}'

    #Send the requestto update the user balance
    r = s.post('http://localhost:5000/api/cdr', json=json.loads(payload),\
            headers={'content-type': 'application/json'})

    #TODO: Handle when the request fail
    if r.ok == False:
        pass

    print from_user.id_
    payload = '{"signal":"-", "type_":"decrease", "value": "'+ str(billsec) +\
            '", "userId":'+ str(from_user.id_) +'}'

    # Send the requestto update the user balance
    r = s.post('http://localhost:5000/api/balance',\
            json=json.loads(payload),\
            headers={'content-type': 'application/json'})

    #TODO: Handle when the request fail
    if r.ok == False:
        pass
    s.close()

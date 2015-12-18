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
from asterisk.agi import AGIAppError
from models import User, CDR, Ballance 
from config import db
agi = asterisk.agi.AGI()

from_user = User.query.filter_by( 
    clid=agi.env['agi_callerid']).first() 
to_user = User.query.filter_by( 
    clid=agi.env['agi_extension']).first()

if agi.get_variable('DIALSTATUS') == 'ANSWER':
    # Time from answer to hangup
    billsec = int(agi.get_variable('CDR(billsec)'))
    # Time the user answered
    answer = datetime.fromtimestamp(float(agi.get_variable('CDR(answer,u)')))
    # Create a new CDR record
    #db.session.add(CDR(answer, billsec, from_user.id_, to_user.id_ ))
   
    # Update user balance
    #from_user.balance -= billsec
#    db.session.add(Ballance(unicode(datetime.now()), 'decrease', billsec, '-', from_user.id_))
    db.session.add(Ballance(date=datetime.now(), type_= 'decrease',signal='-',value=str(billsec),usersId=str(from_user.id_)))
    print datetime.now(),'decrease','-',billsec,from_user.id_
    db.session.commit()
    print "3"

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import db
from models import User, Ballance



admin = User(True,'administrator', 'nowhere', '000','admin', 'adm123', '999999999','999999999999999', '0' ,'0')
guest = User(True,'guest', 'nowhere', '1','guest', '123123', '999999998','999999999999998', '0' ,'0')

db.session.add(admin)
db.session.add(guest)

db.session.commit()

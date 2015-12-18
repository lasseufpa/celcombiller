from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import db
from models import User, Ballance

admin = User('admin', 'adm123', '999999999', True,'999999999999999')
guest = User('guest', '123123', '999999998', False,'000000000000000')

db.session.add(admin)
db.session.add(guest)
db.session.commit()

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import db
from models import User, Ballance

# admin = User('admin', 'adm123', '999999999', '9999', True)
# guest = User('guest', '123123', '999999998', '0000', False)
guest = User('guest3', '123123', '399991998', True)
# admin = User('admin', 'adm123', '999999999', '9999', True)

# db.session.add(admin)
db.session.add(guest)
db.session.commit()

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from apiConfig import db
from models import User

admin = User('admin', 'adm123', '999999999', '9999', True)
guest = users('guest', '123123', '999999999', '0000', False)

db.session.add(admin)
db.session.add(guest)
db.session.commit()
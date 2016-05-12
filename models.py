from config import db, app
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm.session import object_session
from sqlalchemy.dialects.postgresql import ENUM
from datetime import *

row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}

# Create your Flask-SQLALchemy models as usual but with the following two
# (reasonable) restrictions:
#   1. They must have a primary key column of type sqlalchemy.Integer or
#      type sqlalchemy.Unicode.
#   2. They must have an __init__ method which accepts keyword arguments for
#      all columns (the constructor in flask.ext.sqlalchemy.SQLAlchemy.Model
#      supplies such a method, so you don't need to declare a new one).

tunel_table = db.Table('association', db.Model.metadata,
    db.Column('User_id', db.Integer, db.ForeignKey('users.id_')),
    db.Column('Groups_id', db.Integer, db.ForeignKey('groups.id_'))
)

class User(db.Model):
    """
    System users each of which has a unique caller id (CLID)
    """
    __tablename__ = 'users'



    id_         = db.Column(db.Integer, primary_key=True, nullable=False)
    admin       = db.Column(db.Boolean, nullable=False)
    name        = db.Column(db.Unicode, nullable=False)
    adress      = db.Column(db.Unicode)
    cpf         = db.Column(db.Integer, nullable=False)
    username    = db.Column(db.Unicode, nullable=False, unique=True)
    password    = db.Column(db.Unicode, nullable=False)
    clid        = db.Column(db.String(9), nullable=False, unique=True)
    imsi        = db.Column(db.Integer, nullable=False, unique=True)
    voice_balance = db.Column(db.Integer, nullable=False)
    data_balance = db.Column(db.Integer, nullable=False)

    tunel       = db.relationship('Groups', secondary=tunel_table)

    def is_admin(self):
        return self.admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id_)

    def BallanceUser(self):
        return self.voice_balance

    def DataBallanceUser(self):
        return self.data_balance

    @hybrid_property
    def BallanceUserHistoric(self):
        # TODO: Maybe it should use object_session
        balances = Ballance.query.order_by(Ballance.id_.desc()).filter_by(userId=self.id_).limit(10)
        historic_list = []
        for y in balances:
            historic_list.append(row2dict(y))

        return historic_list

    def __init__(self ,  admin, name, adress, cpf, username, password, clid, imsi, voice_balance, data_balance ):
        self.admin  = admin
        self.name   = name   
        self.adress = adress
        self.cpf    = cpf
        self.username   = username
        self.password   = password
        self.clid   = clid
        self.imsi   = imsi
        self.voice_balance = voice_balance
        self.data_balance = data_balance



    def __repr__(self):
        return '<User %r>' % (self.username)

class CDR(db.Model):
    """
    Call Detail Records holds information about finished calls
    """
    __tablename__ = 'cdr'

    id_ = db.Column(db.Integer, db.Sequence('cdr_id_seq'), primary_key=True)
    answer = db.Column(db.DateTime)
    billsec = db.Column(db.Integer)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id_'))
    from_user = db.relationship('User', backref='originated_calls',
                            foreign_keys=from_user_id)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id_'))
    to_user = db.relationship('User', backref='received_calls',
                            foreign_keys=to_user_id)

    def __repr__(self):
        return '<from=%s date=%s duration=%s>' % (self.from_user, self.answer,
                                                  self.billsec)

class Groups(db.Model):
    """
    # Register Credits if
    """
    __tablename__ = 'groups'

    id_ = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    dates_to_update = db.relationship('Dates')
    tunel = db.relationship('User', secondary=tunel_table)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'GROUPS %r' % (self.name)

    @hybrid_property
    def newUser(self):
        return 0

    @newUser.setter
    def newUser(self, userIds):
        for userId in userIds:
            self.tunel.append(User.query.filter_by(id_=userId).first())
            db.session.add(self)
        db.session.commit()

    @hybrid_property
    def removeUser(self):
        return 0

    @removeUser.setter
    def removeUser(self, userIds):
        for userId in userIds:
            self.tunel.remove(User.query.filter_by(id_=userId).first())

    @hybrid_property
    def updateGroup(self):
        return 0

    @updateGroup.setter
    def updateGroup(self, check):
        if check == 1:
            deleteDate = Dates.query.filter_by(group_id=self.id_).first()
            db.session.delete(deleteDate)
            for var in self.tunel:
                db.session.query(User).filter_by(id_=var.id_)\
                    .update({'balance':'1250'})

class Dates(db.Model):

    __tablename__ = 'dates'

    id_ = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id_'))
    date = db.Column(db.DateTime)

    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return 'DATES %r' % (self.id_)



class Ballance(db.Model):

    __tablename__ = 'balance'

    id_     = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id_'))
    date    = db.Column(db.DateTime())
    type_   = db.Column(ENUM('increase', 'decrease'))
    value   = db.Column(db.Integer)
    signal  = db.Column(db.String(1))
    balance   = db.Column(ENUM('voice', 'data'))


    def __init__(self, type_, value,balance, signal, userId,date=None):
        self.date   = datetime.now()
        self.type_  = type_
        self.value  = value
        self.signal = signal
        self.balance = balance
        self.userId = userId

        if balance == 'voice':
            if type_ == 'increase':
                user = db.session.query(User).filter_by(id_=userId).first()
                user.voice_balance = user.data_balance + int(value)
            elif type_ == 'decrease':
                user = db.session.query(User).filter_by(id_=userId).first()
                user.voice_balance = user.data_balance - int(value)
            db.session.commit()
        
        elif balance == 'data':
            if type_ == 'increase':
                user = db.session.query(User).filter_by(id_=userId).first()
                user.data_balance = user.data_balance + int(value)
            elif type_ == 'decrease':
                user = db.session.query(User).filter_by(id_=userId).first()
                user.data_balance = user.data_balance - int(value)
            db.session.commit()


    def __repr__(self):
        return 'balance %r' % (self.id_)




# Create the database tables.
db.create_all()

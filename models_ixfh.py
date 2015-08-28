from apiConfig_ixfh import db, app


# Create your Flask-SQLALchemy models as usual but with the following two
# (reasonable) restrictions:
#   1. They must have a primary key column of type sqlalchemy.Integer or
#      type sqlalchemy.Unicode.
#   2. They must have an __init__ method which accepts keyword arguments for
#      all columns (the constructor in flask.ext.sqlalchemy.SQLAlchemy.Model
#      supplies such a method, so you don't need to declare a new one).
class Admin(db.Model):

    __tablename__ = 'admin'

    id_ = db.Column(db.Integer , primary_key=True)
    username = db.Column(db.String(20), unique=True , index=True)
    password = db.Column(db.String(10))

    def __init__(self , username ,password):
        self.username = username
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id_)

    def __repr__(self):
        return '<User %r>' % (self.username)


class User(db.Model):
    """
    System users each of which has a unique caller id (CLID)
    """
    __tablename__ = 'users'


    id_ = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, unique=True)
    clid = db.Column(db.String(9), nullable=False, unique=True)
    balance = db.Column(db.Float, default=0)

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


# Create the database tables.
db.create_all()
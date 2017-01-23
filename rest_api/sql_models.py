# data tables

from sqlalchemy.orm import relationship, backref
from flask_login import LoginManager, UserMixin, login_required
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context

from sqlalchemy import (
    Column,
    Boolean,
    String,
    Integer,
    Float,
    ForeignKey,
    DateTime)

# from app import db
from app import Base, app

#class Geoposition(db.Model):
class Geoposition(Base):
    __tablename__ = 'geolocation'
    geo_id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float(20))
    longitude = Column(Float(20))
    accuracy = Column(Float(20))
    timestamp = Column(DateTime)


#class Evaluation(db.Model):
class Evaluation(Base):
    __tablename__ = 'gardenevals_evaluations'
    evaluation_id  = Column(Integer, primary_key=True, autoincrement=True)
    garden_id = Column(Integer, ForeignKey('gardenevals_gardens.garden_id'))
    eval_type = Column(String(80))
    scoresheet = Column(String(80))
    completed = Column(Boolean)
    score = Column(Integer)
    rating = Column(String(2))
    ratingyear = Column(Integer)
    evaluator_id = Column(Integer, ForeignKey('garden_evaluators.evaluator_id'))
    evaluator = relationship("Evaluator", backref=backref("evaluation", uselist=False))
    date_evaluated = Column(DateTime)
    comments = Column(String(80))


#class Site(db.Model):
class Site(Base):
    __tablename__ = 'gardenevals_gardens'
    garden_id = Column(Integer, primary_key=True, autoincrement=True)
    geo_id = Column(Integer, ForeignKey('geolocation.geo_id'))
    address = Column(String(80))
    city = Column(String(80))
    state = Column(String(2))
    zip = Column(String(5))
    raingarden = Column(Boolean)
    neighborhood =  Column(String(80))
    county = Column(String(80))
    geoposition = relationship("Geoposition", backref=backref("site", uselist=False))
    evaluations = relationship("Evaluation", backref="site")


#class Person(db.Model):
class Person(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(20))
    lastname = Column(String(15))


#class Evaluator(db.Model):
class Evaluator(Base):
    __tablename__ = 'garden_evaluators'
    evaluator_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)

'''
class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(128))
    person_id = Column(Integer, ForeignKey('users.user_id'))
    person = relationship("Person", backref=backref("user", uselist=False))
   roles = relationship("Role", secondary=lambda: user_roles, backref="user")

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration = 3600): # set expiration to 1 hour
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.username)


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(80))
    city = Column(String(80))
    state = Column(String(2))
    zip = Column(String(5))
    neighborhood =  Column(String(80))
    county = Column(String(80))
'''
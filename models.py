"""
    SQL tables.
    This is a typical declarative usage of sqlalchemy,
    It has no dependency on flask or eve itself. Pure sqlalchemy.
"""
from app import db, app

from flask import _request_ctx_stack, request
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from passlib.apps import custom_app_context as pwd_context
from flask.ext.login import LoginManager, UserMixin, login_required

from sqlalchemy.engine import reflection
from sqlalchemy.engine.reflection import Inspector

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import inspect, join
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, column_property
from sqlalchemy.ext import hybrid
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import Table
from sqlalchemy import func
from sqlalchemy import (
    Column,
    Boolean,
    String,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    Enum)

Base = declarative_base()
Base.metadata.bind = db.engine


#extend LoginManager

class CustomLoginManager(LoginManager):
    def reload_user(self):
        if request.headers.has_key('X-Auth-Token'):
            ctx = _request_ctx_stack.top
            ctx.user = User.query.filter_by(username=request.headers.get('X-Auth-Token')).first()
            return
        # super(CustomLoginManager,self).reload_user()


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship("Person", backref=backref("user", uselist=False))
 #   roles = relationship("Role", secondary=lambda: user_roles, backref="user")

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


class Address(db.Model):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(80))
    city = Column(String(80))
    state = Column(String(2))
    zip = Column(String(5))
    neighborhood =  Column(String(80))
    county = Column(String(80))


class Geoposition(db.Model):
    __tablename__ = 'geoposition'
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(Integer)
    latitude = Column(Float(20))
    longitude = Column(Float(20))
    accuracy = Column(Float(20))
    timestamp = Column(DateTime)


class Site(db.Model):
    __tablename__ = 'site'
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_name  = Column(String(80))# does site have a formal name
    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship("Address", backref=backref("site", uselist=False))
    geoposition_id = Column(Integer, ForeignKey('geoposition.id'))
    geoposition = relationship("Geoposition", backref=backref("site", uselist=False))
    evaluations = relationship("Evaluation", backref="site")
    site_maintainers = relationship("SiteMaintainer", backref="site")


class Evaluation(db.Model):
    __tablename__ = 'evaluation'
    id  = Column(Integer, primary_key=True, autoincrement=True)
    evaluator_id = Column(Integer, ForeignKey('person.id'))
    evaluator = relationship("Person", backref=backref("evaluation", uselist=False))
    site_id = Column(Integer)
    evaluated_when = Column(DateTime)
    exists = Column(Boolean)# does site exist at time of evaluation
    comments = Column(String(80))
    site_id = Column(Integer, ForeignKey('site.id'))


class Person(db.Model):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(20))
    middle_name = Column(String(15))
    last_name = Column(String(15))
    email_id = Column(Integer, ForeignKey('email.id'))
    email = relationship("Email", backref=backref("person", uselist=False))
    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship("Address", backref=backref("person", uselist=False))
    phone_id = Column(Integer, ForeignKey('phone.id'))
    phone = relationship("Phone", backref=backref("person", uselist=False))
    type = Column(Enum("evaluator", "site maintainer", name="person_types"))


class SiteMaintainer(db.Model):
    __tablename__ = 'site_maintainer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(Integer, ForeignKey('site.id'))
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship("Person", backref=backref("site_maintainer", uselist=False))


class Phone(db.Model):
    __tablename__ = 'phone'
    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange = Column(String(10))
    type = Column(Enum("mobile", "business", "home", name = "phone_types"))


class Email(db.Model):
    __tablename__ = 'email'
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(80))# need validator

# now the fun begins:

# evaluation instrument items
class Factor(db.Model):
    __tablename__ = 'factor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum("garden", "rain garden", "permeable pavers", name = "evaluation_types"))
    description = Column(String(80))# instrument item description
    result = Column(String(80))# instrument item value outcome


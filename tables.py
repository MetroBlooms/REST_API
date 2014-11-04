"""
    SQL tables.
    This is a typical declarative usage of sqlalchemy,
    It has no dependency on flask or eve itself. Pure sqlalchemy.
"""
from sqlalchemy import inspect
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


class CommonColumns(Base):
    __abstract__ = True
    _created = Column(DateTime, default=func.now())
    _updated = Column(DateTime, default=func.now(), onupdate=func.now())

    @hybrid_property
    def _id(self):
        """
        Eve backward compatibility
        """
        return self.id

    def jsonify(self):
        """
        Used to dump related objects to json
        """
        relationships = inspect(self.__class__).relationships.keys()
        mapper = inspect(self)
        attrs = [a.key for a in mapper.attrs if \
                a.key not in relationships \
                and not a.key in mapper.expired_attributes]
        attrs += [a.__name__ for a in inspect(self.__class__).all_orm_descriptors if a.extension_type is hybrid.HYBRID_PROPERTY]
        return dict([(c, getattr(self, c, None)) for c in attrs])


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature


class User(Base):
    __tablename__ = 'user'
    name = Column(String, primary_key=True)
    roles = relationship("Role", secondary=lambda: user_roles, backref="user")

    def generate_auth_token(self, expiration=24*60*60):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'login': self.login })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        return data['login']

    def isAuthorized(self, role_names):
        allowed_roles = set([r.id for r in self.roles]).intersection(set(role_names))
        return len(allowed_roles) > 0


class Role(Base):
    __tablename__ = 'role'
    name = Column(String(50), primary_key=True)


user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_name', String, ForeignKey('user.name')),
    Column('role_name', String, ForeignKey('role.name'))
)


class Address(CommonColumns):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(80))
    city = Column(String(80))
    state = Column(String(2))
    zip = Column(String(5))
    neighborhood =  Column(String(80))
    county = Column(String(80))


class Geoposition(CommonColumns):
    __tablename__ = 'geoposition'
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(Integer)
    latitude = Column(Float(20))
    longitude = Column(Float(20))
    accuracy = Column(Float(20))
    timestamp = Column(DateTime)


class Site(CommonColumns):
    __tablename__ = 'site'
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_name  = Column(String(80))# does site have a formal name
    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship("Address", backref=backref("site", uselist=False))
    geoposition_id = Column(Integer, ForeignKey('geoposition.id'))
    geoposition = relationship("Geoposition", backref=backref("geoposition", uselist=False))
    evaluations = relationship("Evaluation", backref="site")
    site_maintainers = relationship("SiteMaintainer", backref="site")


class Evaluation(CommonColumns):
    __tablename__ = 'evaluation'
    id  = Column(Integer, primary_key=True, autoincrement=True)
    evaluator_id = Column(Integer, ForeignKey('person.id'))
    evaluator = relationship("Person", backref=backref("evaluation", uselist=False))
    site_id = Column(Integer)
    evaluated_when = Column(DateTime)
    exists = Column(Boolean)# does site exist at time of evaluation
    comments = Column(String(80))
    site_id = Column(Integer, ForeignKey('site.id'))


class Person(CommonColumns):
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
    type = Column(Enum("evaluator", "site maintainer", name = "person_types"))


class SiteMaintainer(CommonColumns):
    __tablename__ = 'site_maintainer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(Integer, ForeignKey('site.id'))
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship("Person", backref=backref("site_maintainer", uselist=False))


class Phone(CommonColumns):
    __tablename__ = 'phone'
    id = Column(Integer, primary_key=True, autoincrement=True)
    exchange = Column(String(10))
    type = Column(Enum("mobile", "business", "home", name = "phone_types"))


class Email(CommonColumns):
    __tablename__ = 'email'
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(80))# need validator

# now the fun begins:

# evaluation instrument items
class Factor(CommonColumns):
    __tablename__ = 'factor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum("garden", "rain garden", "permeable pavers", name = "evaluation_types"))
    description = Column(String(80))# instrument item description
    result = Column(String(80))# instrument item value outcome

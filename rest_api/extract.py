from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import (
    Column,
    Boolean,
    String,
    Integer,
    Float,
    ForeignKey,
    DateTime,
    Enum)

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

'''
use metroblo_website;

SELECT  latitude,
longitude,
accuracy,
address,
city,
zip,
raingarden,
scoresheet,
score,
eval_type,
rating,
comments,
date_evaluated
FROM gardenevals_evaluations eval
left outer join (gardenevals_gardens garden, geolocation geo)
on (garden.garden_id = eval.garden_id AND garden.geo_id = geo.geo_id)
where completed = 1 AND scoresheet is not null

'''

# from app import app, db
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

Base = declarative_base()
Base.metadata.bind = db.engine


class Geolocation(db.Model):
    __tablename__ = 'geolocation'
    geo_id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float(20))
    longitude = Column(Float(20))
    accuracy = Column(Float(20))
    timestamp = Column(DateTime)

class Gardenevals_evaluation(db.Model):
    __tablename__ = 'gardenevals_evaluations'
    evaluation_id  = Column(Integer, primary_key=True, autoincrement=True)
    garden_id = Column(Integer, ForeignKey('gardenevals_gardens.garden_id'))
    eval_type = Column(String(80))
    scoresheet = Column(String(80))
    score = Column(Integer)
    rating = Column(String(2))
    evaluator_id = Column(Integer, ForeignKey('garden_evaluators.evaluator_id'))
    evaluator = relationship("Garden_evaluators", backref=backref("evaluation", uselist=False))
    date_evaluate = Column(DateTime)
    comments = Column(String(80))

class Gardenevals_gardens(db.Model):
    __tablename__ = 'gardenevals_gardens'
    garden_id = Column(Integer, primary_key=True, autoincrement=True)
    geo_id = Column(Integer, ForeignKey('geolocation.geo_id'))
    address = Column(String(80))
    city = Column(String(80))
    state = Column(String(2))
    zip = Column(String(5))
    neighborhood =  Column(String(80))
    county = Column(String(80))
    geoposition = relationship("Geolocation", backref=backref("site", uselist=False))
    evaluations = relationship("Gardenevals_evaluation", backref="site")

'''
class Person(db.Model):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(20))
    lastname = Column(String(15))
    email = Column(String)
'''

class Garden_evaluators(db.Model):
    __tablename__ = 'garden_evaluators'
    evaluator_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)



query = db.session.query(Geolocation)

out = []
for result in query:
            data = {'geo_id': result.geo_id}

            out.append(data)


print 'OUT'
print out

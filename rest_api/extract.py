from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import and_

from sqlalchemy.orm import relationship, backref
from sqlalchemy import (
    Column,
    Boolean,
    String,
    Integer,
    Float,
    ForeignKey,
    DateTime)

import tempfile
import os
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()

import pandas as pd

from phpserialize import unserialize

# from app import app, db
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# data tables
# TODO: give more succinct class names
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
    completed = Column(Boolean)
    score = Column(Integer)
    rating = Column(String(2))
    evaluator_id = Column(Integer, ForeignKey('garden_evaluators.evaluator_id'))
    evaluator = relationship("Garden_evaluators", backref=backref("evaluation", uselist=False))
    date_evaluated = Column(DateTime)
    comments = Column(String(80))

class Gardenevals_gardens(db.Model):
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
    geoposition = relationship("Geolocation", backref=backref("site", uselist=False))
    evaluations = relationship("Gardenevals_evaluation", backref="site")

class Garden_evaluators(db.Model):
    __tablename__ = 'garden_evaluators'
    evaluator_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)

'''
class Person(db.Model):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(20))
    lastname = Column(String(15))
    email = Column(String)
'''

'''
SQL Query:

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

# create SQLAlchemy query object
query = db.session.query(Gardenevals_gardens.address,
                         Gardenevals_gardens.city,
                         Gardenevals_gardens.zip,
                         Gardenevals_evaluation.scoresheet,
                         Gardenevals_evaluation.score,
                         Gardenevals_evaluation.rating,
                         Geolocation.latitude,
                         Geolocation.longitude,
                         Geolocation.accuracy,
                         Gardenevals_gardens.raingarden,
                         Gardenevals_evaluation.eval_type,
                         Gardenevals_evaluation.comments,
                         Gardenevals_evaluation.date_evaluated,
                         Gardenevals_evaluation.evaluator_id).\
    join(Gardenevals_evaluation, Gardenevals_gardens.garden_id == Gardenevals_evaluation.garden_id).\
    outerjoin(Geolocation, Geolocation.geo_id == Gardenevals_gardens.geo_id).\
    filter(and_(Gardenevals_evaluation.completed == 1,
                Gardenevals_evaluation.scoresheet != None,
                Gardenevals_gardens.raingarden == 1))


# get data set as pandas frame
frame = pd.read_sql(query.statement, query.session.bind)

print frame

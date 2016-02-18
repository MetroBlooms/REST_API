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
pd.set_option('display.width', 1000)

from phpserialize import unserialize
import simplejson as json

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

class Evaluation(db.Model):
    __tablename__ = 'gardenevals_evaluations'
    evaluation_id  = Column(Integer, primary_key=True, autoincrement=True)
    garden_id = Column(Integer, ForeignKey('gardenevals_gardens.garden_id'))
    eval_type = Column(String(80))
    scoresheet = Column(String(80))
    completed = Column(Boolean)
    score = Column(Integer)
    rating = Column(String(2))
    evaluator_id = Column(Integer, ForeignKey('garden_evaluators.evaluator_id'))
    evaluator = relationship("Site_evaluators", backref=backref("evaluation", uselist=False))
    date_evaluated = Column(DateTime)
    comments = Column(String(80))

class Site(db.Model):
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
    evaluations = relationship("Evaluation", backref="site")

class Evaluator(db.Model):
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
query = db.session.query(Site.address,
                         Site.city,
                         Site.zip,
                         Evaluation.scoresheet,
                         Evaluation.score,
                         Evaluation.rating,
                         Geolocation.latitude,
                         Geolocation.longitude,
                         Geolocation.accuracy,
                         Site.raingarden,
                         Evaluation.eval_type,
                         Evaluation.comments,
                         Evaluation.date_evaluated,
                         Evaluation.evaluator_id).\
    join(Evaluation, Site.garden_id == Evaluation.garden_id).\
    outerjoin(Geolocation, Geolocation.geo_id == Site.geo_id).\
    filter(and_(Evaluation.completed == 1,
                Evaluation.scoresheet != None,
                Site.raingarden == 1))

# serialize query output as list of dictionaries; convert scoresheet from php array object to list of dictionaries
out = []
for result in query:
            data = {'php_serialization': result.scoresheet,
                    'jsonified': json.dumps(unserialize(result.scoresheet.replace(' ', '_').lower()))}

            out.append(data)

print out[1:2]
print out[100:101]
print out[300:301]
print out[700:701]

# get data set as pandas frame for manipulation

#frame = pd.read_sql(query.statement, query.session.bind)

#print frame

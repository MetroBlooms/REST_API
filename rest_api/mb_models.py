# data tables

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.orm import relationship, backref
from sqlalchemy import (
    Column,
    Boolean,
    String,
    Integer,
    Float,
    ForeignKey,
    DateTime)

from rest_api.app import app, db
app.config.from_object('rest_api.config')

# TODO: give more succinct class names
class Geoposition(db.Model):
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


#!venv/bin/python

from app import Base, e # db


Base.metadata.create_all(bind=e)

# Create db
#db.create_all()


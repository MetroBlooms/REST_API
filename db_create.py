#!venv/bin/python
import os.path

from app import db


# Create db
db.create_all()


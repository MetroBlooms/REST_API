#!venv/bin/python
import os.path

from app import db, app


# Create db
db.create_all()


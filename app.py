# Create db connection to postgres
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# Define Flask app
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# import models as a subclass
import models, views







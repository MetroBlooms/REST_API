# Create db connection to postgres
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask.ext import restful
from flask_cors import CORS

# Define Flask app
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


# create api isntance
api = restful.Api(app)

# creatre mail instance
mail = Mail(app)
# import models as a subclass

cors = CORS(app, headers="X-Requested-With, Content-Type")


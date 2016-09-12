# Create db connection to postgres
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Define Flask app
app = Flask(__name__)
app.config.from_object('config')
#app.config.from_object('config')
db = SQLAlchemy(app)

# import models as a subclass
import sql_models, views

# import models as a subclass

cors = CORS(app, headers="X-Requested-With, Content-Type")


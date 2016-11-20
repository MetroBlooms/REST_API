# Create db connection to postgres
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base



# Define Flask app
app = Flask(__name__)
app.config.from_object('config')
#app.config.from_object('config')
#db = SQLAlchemy(app)

e = create_engine("sqlite:////Users/gregsilverman/development/data/mb_analytics.db", echo=True)
s = Session(e)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=e))
Base = declarative_base()
Base.query = db_session.query_property()
Base.metadata.create_all(e)
# import models as a subclass
#import sql_models, views
import sql_models

cors = CORS(app, headers="X-Requested-With, Content-Type")


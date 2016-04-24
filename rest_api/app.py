# Create db connection to postgres
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask_cors import CORS
from security.email.email_config import EmailConfig
import config

# Define Flask app
app = Flask(__name__)
app.config.from_object(config)
#app.config.from_object('config')
db = SQLAlchemy(app)

# import models as a subclass
import sql_models, views

# import models as a subclass
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465

emailConfig = EmailConfig()
username = emailConfig.get_account_recovery_username()
# app.config['MAIL_DEFAULT_SENDER'] = username
app.config['MAIL_USERNAME'] = username
app.config['MAIL_PASSWORD'] = emailConfig.get_account_recovery_password()
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

cors = CORS(app, headers="X-Requested-With, Content-Type")


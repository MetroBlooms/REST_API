import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Prevent cross-site request forgery
WTF_CSRF_ENABLED = True

# Dummy secret key so we can use sessions - use with CSRF
SECRET_KEY = '123456790'

# db connection string to postgres
#SQLALCHEMY_DATABASE_URI = 'postgres://test:test@localhost/test'
SQLALCHEMY_DATABASE_URI = 'mysql://gms:test@localhost/test'
SQLALCHEMY_ECHO = True

# Flask-Mail configuration

# After 'Create app'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = '@gmail.com'
MAIL_PASSWORD = ''

# CORS headers with JSON
#CORS_HEADERS = 'Content-Type'
#token
#CORS_HEADERS = 'X-Auth-Token'
CORS_HEADERS = 'Authorization, Content-Type, X-Auth-Token, X-Requested-With'
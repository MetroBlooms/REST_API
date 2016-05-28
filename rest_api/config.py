import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Prevent cross-site request forgery
WTF_CSRF_ENABLED = True

# Dummy secret key so we can use sessions - use with CSRF
SECRET_KEY = '123456790'

# db connection string to postgres
SQLALCHEMY_DATABASE_URI = 'mysql://gms:test@localhost/nestedSetsPOC'
SQLALCHEMY_ECHO = True

# CORS headers with JSON
CORS_HEADERS = 'Authorization, Content-Type, X-Auth-Token, X-Requested-With'
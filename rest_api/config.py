import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Prevent cross-site request forgery
WTF_CSRF_ENABLED = True

# Dummy secret key so we can use sessions - use with CSRF
SECRET_KEY = '123456790'

# db connection string to postgres
#SQLALCHEMY_DATABASE_URI = 'mysql://gms:test123@localhost/metroblo_website'
# using bdb w/ SQL API

SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/gregsilverman/development/data/mb_analytics.db'
#SQLALCHEMY_ECHO = False
#SQLALCHEMY_TRACK_MODIFICATIONS = False

# CORS headers with JSON
#CORS_HEADERS = 'Content-Type'
#token
#CORS_HEADERS = 'X-Auth-Token'
CORS_HEADERS = 'Authorization, Content-Type, X-Auth-Token, X-Requested-With'

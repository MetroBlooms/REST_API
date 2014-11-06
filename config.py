import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Create dummy secrey key so we can use sessions
SECRET_KEY = '123456790'

# Create db connection to postgres
SQLALCHEMY_DATABASE_URI = 'postgres://test:test@localhost/test'
SQLALCHEMY_ECHO = True
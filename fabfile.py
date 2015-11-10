from fabric.api import *
from contextlib import contextmanager

env.directory = '~/development/python/rest-api/rest_api'
env.activate = 'source ' + env.directory + '/venv/bin/activate' # use virtual environment to execute commands

# set context manager to use virtualenv
@contextmanager
def virtualenv():
    with cd(env.directory):
        with prefix(env.activate):
            yield

def call( cmd):
   local( cmd, shell="/bin/bash")

# set up environment prior to dev
def prepare():
     with virtualenv():
        call('git pull')
        call('/bin/bash venv/bin/activate')
        call('pip freeze')
        call('pip install -r requirements.txt')
        # ensure correct python from virtual environment is being used
        call('which python')

# create db structure from models
def db():
     with virtualenv():
        call('which python')
        call('./db_create.py')

# make API available
def api():
    with virtualenv():
        call('./api.py')
        call('which python')

# push change to repo
def scm():
    call('git add --all')
    call('git commit')
    call('git push origin master')


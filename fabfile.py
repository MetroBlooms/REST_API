from fabric.api import *
from contextlib import contextmanager

env.directory = '~/development/python/rest-api'
env.activate = 'source ' + env.directory + '/venv/bin/activate' # use virtual environment to execute commands

# set context manager to use virtualenv
@contextmanager
def virtualenv():
    with cd(env.directory):
        with prefix(env.activate):
            yield

# set up environment prior to dev
def prepare():
     with virtualenv():
        local('git pull')
        local('/bin/bash venv/bin/activate')
        local('pip freeze')
        local('pip install -r requirements.txt')
        # ensure correct python from virtual environment is being used
        local('which python')

# create db structure from models
def db_create():
     with virtualenv():
        local('which python')
        local('./db_create.py')

# make API available
def api():
    with virtualenv():
        local('which python')
        local('./api.py')
        local('which python')


def scm():
    local('git add --all')
    local('git commit')
    local('git push')
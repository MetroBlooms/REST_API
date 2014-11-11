from fabric.api import *
from contextlib import contextmanager

env.directory = '/Users/gregsilverman/development/python/rest-api'
env.activate = 'source ' + env.directory + '/venv/bin/activate' # use virtual environment to execute commands

@contextmanager
def virtualenv():
    with cd(env.directory):
        with prefix(env.activate):
            yield

def prepare():
     with virtualenv():
        local('git pull')
        local('/bin/bash venv/bin/activate')
        local('pip freeze')
        local('pip install -r requirements.txt')
        # ensure correct python from virtual environment is being used
        local('which python')

def db_create():
     with virtualenv():
        local('which python')
        local('./db_create.py')

def api():
    with virtualenv():
        local('which python')
        local('./api.py')
        local('which python')


def scm():
    local('git add --all')
    local('git commit')
    local('git push')
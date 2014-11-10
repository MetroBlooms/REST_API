from fabric.api import local, path, cd, prefix
from contextlib import contextmanager

project_dir = '~/development/python/rest-api'
env_bin_dir = project_dir + '/venv/bin' # use virtual environment to execute commandsi


def prepare():
     with path(env_bin_dir, behavior='prepend'):
        local('git pull')
        local('/bin/bash venv/bin/activate')
        local('pip freeze')
        local('pip install -r requirements.txt')
        # ensure correct python from virtual environment is being used
        local('which python')

def scm():
    local('git add --all')
    local('git commit')
    local('git push')
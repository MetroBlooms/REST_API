s, sys, logging

#PROJECT_DIR = '/var/www/wsgi/rest_api/rest_api/'
#PROJECT_DIR = '/Library/WebServer/wsgi/rest_api/rest_api/'
PROJECT_DIR = '~/development/python/rest_api/restapi'

activate_this = os.path.join(PROJECT_DIR + 'venv', 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
sys.path.insert(0, PROJECT_DIR)

from api import app as application
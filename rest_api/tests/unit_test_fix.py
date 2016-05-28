# NOTE: 05-28-2016: fletch22: This is a fix for a unit test challenge in PyCharm. When the unit test is run within PyCharm it cannot find
# many of the modules. The reason: The unit tests run from the project root "REST_API". Note the upper case spelling.
# The application when running as a
# web application runs from the child folder "rest_api". Module import pathing are different for the 2 different contexts. For example,
# when the system is running in the web application context, the path "from rest_api.security.email.email_recovery import EmailRecovery"
# has no meaning -- Python doesn't recognize the module name "rest_api".
# The code below affects only unit tests and fixes the problem by adding the rest_api folder to sys.path. Python is then able to
# discover resources in the "rest_api" package folder. Imports like "from app import app" can then make sense to Python.
# There needs to be a better long term solution for this problem. Perhaps adding to a parent test class?
import sys, os
sys.path.insert(0, os.path.abspath("../../../"))


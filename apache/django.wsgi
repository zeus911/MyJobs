import os, sys

import newrelic.agent
newrelic.agent.initialize('/home/web/MyJobs/MyJobs/newrelic.ini')

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../")
PROJECT_DIR_PARENT = os.path.join(PROJECT_DIR, "../")
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)
if PROJECT_DIR_PARENT not in sys.path:
    sys.path.append(PROJECT_DIR_PARENT)

os.environ['CELERY_LOADER'] = 'django'

import django.core.handlers.wsgi

def application(environ, start_response):
    os.environ['DJANGO_SETTINGS_MODULE'] = environ['DJANGO_SETTINGS_MODULE']
    os.environ['NEW_RELIC_APP_NAME'] = environ['NEW_RELIC_APP_NAME']
    newrelic.app_name = environ['NEW_RELIC_APP_NAME']
    _application = django.core.handlers.wsgi.WSGIHandler()
    _application = newrelic.agent.wsgi_application(application=newrelic.app_name)(_application)
    return _application(environ, start_response)

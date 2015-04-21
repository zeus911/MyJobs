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
_application = django.core.handlers.wsgi.WSGIHandler()
_application = newrelic.agent.wsgi_application()(_application)


def application(environ, start_response):
    os.environ['DJANGO_SETTINGS_MODULE'] = environ['DJANGO_SETTINGS_MODULE']
    return _application(environ, start_response)
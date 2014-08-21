apiimport os, sys

PROJECT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"../")
PROJECT_DIR_PARENT = os.path.join(PROJECT_DIR, "../")
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)
if PROJECT_DIR_PARENT not in sys.path:
    sys.path.append(PROJECT_DIR_PARENT)

os.environ['CELERY_LOADER'] = 'django'
os.environ['DJANGO_SETTINGS_MODULE'] = 'directseo.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

# Add try/except to import and set monitor.py locally.
# Monitor.py detect changes to django project files
# and automatically restarts the django process so
# changes are seen in real-time without the need to
# restart apache/wsgi manually.

try:
    import directseo.monitor
    directseo.monitor.start(interval=1.0)
except ImportError:
    pass

from celery import Celery
from celery.task import task
from datetime import date, timedelta

from api.models import Search
from import_jobs import (clear_solr, clear_for_jsid, import_from_url,
                         refresh_bunit_jobs)

celery = Celery('api.tasks', broker='amqp://')

@task(name='tasks.task_update_solr')
def task_update_solr(jsid):
    """
    Uploads jobs from a url.

    """
    try:
        import_from_url(jsid)
    except:
        raise task_update_solr.retry()

@task(name='tasks.task_refresh_bunit_jobs')
def task_refresh_bunit_jobs(jsid):
    """
    Deletes and re-adds all jobs for a jsid.

    """
    try:
        refresh_bunit_jobs(jsid)
    except:
        raise task_refresh_bunit_jobs.retry()

@task(name="tasks.task_clear_solr")
def task_clear_solr():
    try:
        clear_solr()
    except:
        raise task_clear_solr.retry()

@task(name="tasks.task_clear")
def task_clear(jsid):
    try:
        clear_for_jsid(jsid)
    except:
        raise task_clear.retry()


@task(name='tasks.clean_searches')
def task_clean_searches():
    one_week_ago = date.today() - timedelta(days=7)
    Search.objects.filter(date_last_accessed__lte=one_week_ago).delete()
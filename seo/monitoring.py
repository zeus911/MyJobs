
from datetime import timedelta

from celery.events.snapshot import Polaroid
from django.core.mail import send_mail


class TaskMonitoringCam(Polaroid):

    def on_shutter(self, state):
        """Every `self.freq` collate and review the events celery has generated.
        :Input:
            :state: A state object containing the collected events
        """
        
        interval = timedelta(seconds=self.freq)
        if len(list(state.tasks_by_type('task_etl_to_solr'))) == 0:
            print "No etl_to_solr tasks discovered."
            send_mail('Celery tasks do not appear to be executing', 
                      'Warning, no task_etl_to_solr tasks have been recorded for the last %s.  ' % (str(interval)),
                      'monitoring@my.jobs',
                      ['aws@directemployers.org'], 
                      fail_silently=False)
import datetime

from django.conf import settings


class MockLog(object):
    """
    Mocks only the functionality of Boto keys that we need - currently just
    reading one file into another
    """
    def __init__(self, log_type='analytics', delta=None):
        """
        Inputs:
        :log_type: Type of log to be created; Default: analytics
        :delta: Time delta from now that this log should be timestamped; Delta
            will be added to now - a negative delta is in the past, positive is
            in the future
        """
        self.log_type = log_type
        self.key = 'ip-127-0-0-1/%s/ex-140101000000.log' % log_type
        self.delta = delta

    def get_contents_to_file(self, fp):
        log_file = settings.PROJ_ROOT + '/solr/tests/fake_%s_log' %\
            (self.log_type, )
        with open(log_file) as f:
            contents = f.read()
            date = datetime.datetime.now()
            if self.delta is not None:
                date += self.delta
            contents = contents.format(timestamp=date.strftime("%Y-%m-%d %H:%M:%S"))
            fp.write(contents)
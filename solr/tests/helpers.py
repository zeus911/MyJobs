from django.conf import settings


class MockLog(object):
    """
    Mocks only the functionality of Boto keys that we need - currently just
    reading one file into another
    """
    def __init__(self, log_type='analytics'):
        self.log_type = log_type
        self.key = 'ip-127-0-0-1/%s/ex-140101000000.log' % log_type

    def get_contents_to_file(self, file):
        log_file = settings.PROJ_ROOT + '/solr/tests/fake_%s_log' % self.log_type
        with open(log_file) as f:
            file.write(f.read())
from django.conf import settings


class MockLog(object):
    """
    Mocks only the functionality of Boto keys that we need - currently just
    reading one file into another
    """
    def __init__(self, log_type='analytics'):
        self.key = 'ip-127-0-0-1/%s/ex-140101000000.log' % log_type

    @staticmethod
    def get_contents_to_file(file):
        with open(settings.PROJ_ROOT + '/solr/tests/fakelog') as f:
            file.write(f.read())
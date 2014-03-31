import logging

from django.test.simple import DjangoTestSuiteRunner
from django.conf import settings


class SilentTestRunner(DjangoTestSuiteRunner):

    def run_tests(self, test_labels=None, extra_tests=None, **kwargs):
        logging.disable(logging.CRITICAL)

        if not test_labels:
            test_labels = settings.PROJECT_APPS

        return super(SilentTestRunner, self).run_tests(test_labels,
                                                       extra_tests, **kwargs)

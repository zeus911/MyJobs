import datetime
import os.path
import pysolr

from django.conf import settings
from django.test import TestCase

from api import xmlparse, import_jobs


class JobFeedTestCase(TestCase):
    """
    Test of the JobFeed class using import_jobs.

    """
    fixtures = ['test_data.json']

    def setUp(self):
        settings.SOLR_LOCATION = settings.TESTING_SOLR_LOCATION
        self.solr = pysolr.Solr(settings.SOLR_LOCATION)
        self.testdir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                    'data')
        self.feed = os.path.join(self.testdir, 'dseo_feed_1.xml')

    def tearDown(self):
        import_jobs.clear_solr()
        self.assertEqual(self.solr.search('*:*').hits, 0)

    def test_feed_creation(self):
        feed = xmlparse.JobFeed(self.feed)
        jobs = feed.solr_jobs()
        self.assertEqual(len(jobs), 2)

    def test_file_import(self):
        import_jobs.import_from_file(self.feed, testing=True)
        result = self.solr.search(q="*:*")
        self.assertGreater(result.hits, 0)

    def test_moc(self):
        """
        Confirms that onets are being correctly translated to mocs on
        import.

        """
        import_jobs.import_from_file(self.feed, testing=True)
        result = self.solr.search(q="moc:mmmm")
        self.assertGreater(result.hits, 0)

    def test_date_added(self):
        feed = xmlparse.JobFeed(self.feed)
        jobs = feed.solr_jobs()
        date_added = jobs[0]['date_added']
        self.assertEqual(str(date_added.date()),
                         str(datetime.datetime.now().date()))


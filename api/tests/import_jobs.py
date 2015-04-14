import pysolr

from django.conf import settings
from django.test import TestCase

from api.import_jobs import clear_solr, update_solr


class ImportTests(TestCase):
    def setUp(self):
        settings.SOLR_LOCATION = settings.TESTING_SOLR_LOCATION
        self.solr = pysolr.Solr(settings.SOLR_LOCATION)
        self.buid = 999999

    def tearDown(self):
        clear_solr()
        self.assertEqual(self.solr.search('*:*').hits, 0)

    def test_update_solr_with_existing(self):
        """
        Existing data should be removed on update if it's not in the
        new dataset.

        """
        old_id = 999999
        existing_data = {'buid': self.buid, 'id': old_id, 'guid': '123456'}
        self.solr.add([existing_data])
        new_data = {'buid': self.buid, 'id': 123456, 'guid': 'abcdef'}
        update_solr([new_data], self.buid)
        self.assertEqual(self.solr.search('id:%s' % old_id).hits, 0)

    def test_update_solr_overwrite(self):
        """
        Existing data should be overwritten by new data if the id is
        the same.

        """
        update_id = 111111
        old_guid = 'abcdef'
        new_guid = '123456'
        data = {'buid': self.buid, 'id': update_id, 'guid': old_guid}

        self.solr.add([data])
        data['guid'] = new_guid
        update_solr([data], self.buid)

        self.assertEqual(self.solr.search('guid:%s' % old_guid).hits, 0)
        self.assertEqual(self.solr.search('guid:%s' % new_guid).hits, 1)
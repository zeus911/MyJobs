import datetime
import pytz
import uuid

from django.test import TestCase

from MyJobs.myjobs.models import User
from MyJobs.myjobs.tests.factories import UserFactory
from MyJobs.myprofile.tests.factories import PrimaryNameFactory, AddressFactory
from MyJobs.mysearches.models import SavedSearch
from MyJobs.mysearches.tests.factories import SavedSearchFactory
from MyJobs.solr.models import Update
from MyJobs.solr.helpers import Solr
from MyJobs.solr.signals import profileunits_to_dict, object_to_dict
from MyJobs.solr.tests.helpers import MockLog
from MyJobs.tasks import update_solr_task, parse_log


class SolrTests(TestCase):
    def tearDown(self):
        Solr().delete()

    def test_adding_and_deleting_signals(self):
        """
        Adds and deletes ProfileUnits, Users, and SavedSearches to confirm that
        they are being correctly flagged for addition to and deletion from solr
        and runs add/deletion task to confirm that they are being properly
        added to and deleted from solr.

        """
        Solr().delete()
        user = UserFactory(email="example@example.com")
        PrimaryNameFactory(user=user)

        for i in range(5):
            # Create 5 new users
            user = UserFactory(email='example%s@example.com' % i)
            for search in ['django', 'python', 'programming']:
                # Create 15 new searches and assign three per user
                SavedSearchFactory(user=user,
                                   url='http://test.jobs/search?q=%s' % search,
                                   label='%s Jobs' % search)
        # 6 Users + 15 SavedSearches + 1 ProfileUnit = 22
        self.assertEqual(Update.objects.all().count(), 22)
        update_solr_task('http://127.0.0.1:8983/solr/myjobs_test/')
        self.assertEqual(Solr().search().hits, 22)
        SavedSearch.objects.all().delete()
        update_solr_task('http://127.0.0.1:8983/solr/myjobs_test/')
        self.assertEqual(Solr().search().hits, 7)
        User.objects.all().delete()
        update_solr_task('http://127.0.0.1:8983/solr/myjobs_test/')
        self.assertEqual(Solr().search().hits, 0)

    def test_profileunit_to_dict(self):
        """
        Confirms that a solr dictionary is being generated as expected by
        the profileunits_to_dict function.

        """
        expected = {
            "Name_content_type_id": [25],
            "Name_given_name": ["Alice"],
            "uid": "23##1",
            "ProfileUnits_user_id": 1,
            "Name_user_id": [1],
            "Name_id": [1],
            "Name_family_name": ["Smith"],
            "Name_primary": [True],
        }

        user = UserFactory(email="example@example.com")
        PrimaryNameFactory(user=user)

        result = profileunits_to_dict(user.id)

        self.assertEqual(result['Name_id'], expected['Name_id'])
        self.assertEqual(result['uid'], expected['uid'])

    def test_user_to_dict(self):
        """
        Confirms that a solr dictionary is being generated as expected by
        the object_to_dict function for Users.

        """
        expected = {
            'User_is_superuser': False,
            u'User_id': 1,
            'uid': '18##1',
            'User_is_active': True,
            'User_user_guid': 'c1cf679c-86f8-4bce-bf1a-ade8341cd3c1',
            'User_is_staff': False, 'User_first_name': u'',
            'User_gravatar': 'alice@example.com',
            'User_last_name': u'',
            'User_is_disabled': False,
            'User_opt_in_myjobs': True,
            'User_profile_completion': 0,
            'User_opt_in_employers': True,
            'User_email': 'example@example.com',
        }

        user = UserFactory(email="example@example.com")
        result = object_to_dict(User, user)

        # Exact dictionary comparisons can't be made because of the datetime
        # fields, so compare a few fields instead.
        self.assertEqual(expected['uid'], result['uid'])
        self.assertEqual(expected['User_email'], result['User_email'])

    def test_savedsearch_to_dict(self):
        """
        Confirms that a solr dictionary is being generated as expected by
        the object_to_dict function for SavedSearch.

        """
        expected = {'User_is_superuser': False,
                    'uid': '35##1',
                    'User_is_staff': False,
                    'SavedSearch_day_of_month': None,
                    'User_is_disabled': False,
                    'SavedSearch_last_sent': None,
                    'User_email': 'example@example.com',
                    'SavedSearch_feed': 'http://www.my.jobs/jobs/feed/rss?',
                    'SavedSearch_is_active': True,
                    'SavedSearch_label': 'All Jobs',
                    'User_user_guid': '9ba19d0d-6ee1-4032-a2b8-50a1fc4c1ab5',
                    u'SavedSearch_id': 1,
                    'SavedSearch_email': 'alice@example.com',
                    'SavedSearch_notes': 'All jobs from www.my.jobs',
                    'SavedSearch_frequency': 'W', u'User_id': 1,
                    'User_gravatar': 'alice@example.com',
                    'User_last_name': u'',
                    'SavedSearch_user_id': 1,
                    'User_opt_in_myjobs': True,
                    'User_profile_completion': 0,
                    'SavedSearch_day_of_week': '1',
                    'User_is_active': True,
                    'User_first_name': u'',
                    'SavedSearch_url': 'http://www.my.jobs/jobs',
                    'User_opt_in_employers': True,
                    'SavedSearch_sort_by': 'Relevance'
        }

        user = UserFactory(email="example@example.com")
        search = SavedSearchFactory(user=user)
        result = object_to_dict(SavedSearch, search)

        # Exact dictionary comparisons can't be made because of the datetime
        # fields, so compare a few fields instead.
        self.assertEqual(expected['uid'], result['uid'])
        self.assertEqual(expected['User_email'], result['User_email'])
        self.assertEqual(expected['SavedSearch_url'], result['SavedSearch_url'])

    def test_address_slabs(self):
        expected = {
            'Address_content_type_id': [26],
            'Address_address_line_two': [u'Apt. 8'],
            u'Address_id': [1],
            'uid': '23##1',
            'ProfileUnits_user_id': 1,
            'Address_country_code': [u'USA'],
            'Address_region': [u'USA##IN'],
            'Address_country_sub_division_code': [u'IN'],
            'Address_postal_code': [u'12345'],
            'Address_address_line_one': [u'1234 Thing Road'],
            'Address_user_id': [1],
            'Address_label': [u'Home'],
            'Address_full_location': [u'USA##IN##Indianapolis'],
            'Address_city_name': [u'Indianapolis']
        }

        user = UserFactory(email="example@example.com")
        AddressFactory(user=user)
        result = profileunits_to_dict(user.id)

        self.assertEqual(expected['Address_country_code'],
                         result['Address_country_code'])
        self.assertEqual(expected['Address_region'],
                         result['Address_region'])
        self.assertEqual(expected['Address_full_location'],
                         result['Address_full_location'])

    def test_presave_ignore(self):
        user = UserFactory(email="test@test.test")
        update_solr_task('http://127.0.0.1:8983/solr/myjobs_test/')

        user.last_login = datetime.datetime(2011, 8, 15, 8, 15, 12, 0, pytz.UTC)
        user.save()

        self.assertEqual(Update.objects.all().count(), 0)

        user.last_login = datetime.datetime(2013, 8, 15, 8, 15, 12, 0, pytz.UTC)
        user.email = "test1@test1.test1"
        user.save()

        self.assertEqual(Update.objects.all().count(), 1)

    def test_apache_log_parsing(self):
        """
        Ensure that analytics logs are parsed and stored in solr correctly
        """
        log = MockLog()
        parse_log([log], 'http://127.0.0.1:8983/solr/myjobs_test/')

        solr = Solr()
        results = solr.search(q='uid:analytics*')
        self.assertEqual(results.hits, 1)
        multi_fields = ['facets', 'search_keywords']
        for field in multi_fields:
            self.assertEqual(len(results.docs[0][field]), 2)
        for field in results.docs[0].keys():
            if field not in multi_fields:
                self.assertTrue(type(results.docs[0][field] != list))
        uuid.UUID(results.docs[0]['aguid'])
        with self.assertRaises(KeyError):
            results.docs[0]['User_user_guid']


        solr.delete()
        user = UserFactory()
        user.user_guid = '1e5f7e122156483f98727366afe06e0b'
        user.save()
        parse_log([log], 'http://127.0.0.1:8983/solr/myjobs_test/')
        results = solr.search(q='uid:analytics*')
        for guid in ['aguid', 'User_user_guid']:
            uuid.UUID(results.docs[0][guid])

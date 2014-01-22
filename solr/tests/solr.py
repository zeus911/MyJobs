import datetime

from django.test import TestCase

from myjobs.models import User
from myjobs.tests.factories import UserFactory
from myprofile.tests.factories import PrimaryNameFactory
from mysearches.models import SavedSearch
from mysearches.tests.factories import SavedSearchFactory
from MyJobs.solr.models import Update
from MyJobs.solr.helpers import Solr
from MyJobs.solr.signals import profileunits_to_dict, object_to_dict
from tasks import add_to_solr_task, delete_from_solr_task


class SolrTests(TestCase):
    maxDiff = None
    def setUp(self):
        pass

    def test_adding_and_deleting_signals(self):
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
        add_to_solr_task('http://127.0.0.1:8983/solr/myjobs_test/')
        self.assertEqual(Solr().search().hits, 22)
        SavedSearch.objects.all().delete()
        delete_from_solr_task('http://127.0.0.1:8983/solr/myjobs_test/')
        self.assertEqual(Solr().search().hits, 7)
        User.objects.all().delete()
        delete_from_solr_task('http://127.0.0.1:8983/solr/myjobs_test/')
        self.assertEqual(Solr().search().hits, 0)

    def test_profileunit_to_dict(self):
        expected = {
            "Name_content_type_id": [25],
            "Name_given_name": ["Alice"],
            "uid": "24#1",
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
        expected = {'User_is_superuser': False,
                    u'User_id': 1,
                    'uid': '19#1',
                    'User_is_active': True,
                    'User_user_guid': 'c1cf679c-86f8-4bce-bf1a-ade8341cd3c1',
                    'User_is_staff': False, 'User_first_name': u'',
                    'User_gravatar': 'alice@example.com',
                    'User_last_name': u'',
                    'User_is_disabled': False,
                    'User_opt_in_myjobs': True,
                    'User_profile_completion': 0,
                    'User_opt_in_employers': True,
                    'User_email': 'example@example.com'
        }
        user = UserFactory(email="example@example.com")
        result = object_to_dict(User, user)

        self.assertEqual(expected['uid'], result['uid'])
        self.assertEqual(expected['User_email'], result['User_email'])

    def test_savedsearch_to_dict(self):
        expected = {'User_is_superuser': False,
                    'uid': '36#1',
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

        self.assertEqual(expected['uid'], result['uid'])
        self.assertEqual(expected['User_email'], result['User_email'])
        self.assertEqual(expected['SavedSearch_url'], result['SavedSearch_url'])

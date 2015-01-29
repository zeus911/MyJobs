"""Tests associated with the various MyReports views."""

import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import UserFactory
from mypartners.tests.factories import ContactRecordFactory

class MyReportsTestCase(TestCase):
    """
    Base class for all MyReports Tests. Identical to `django.test.TestCase`
    except that it provides a MyJobs TestClient instance and a logged in user.
    """
    def setUp(self):
        self.client = TestClient()
        # TODO: on release of MyReports, change this to set more appropriate
        #       permissions
        self.user = UserFactory(email="testuser@directemployers.org",
                                is_staff=True)
        self.client.login_user(self.user)


class TestReports(MyReportsTestCase):
    """Tests the reports view, which is the landing page for reports."""

    def test_access_restricted_to_staff(self):
        """Until release, MyReports should only be viewable by staff users."""

        self.user.is_staff = False
        self.user.save()
        response = self.client.get(reverse('reports'))

        self.assertEqual(response.status_code, 404)


class TestSearchRecords(MyReportsTestCase):
    """
    Tests the `search_records` view which is used to query various models.
    """

    def test_json_output(self):
        """Test that filtering partners through ajax works properly."""

        # records to be found in result
        ContactRecordFactory.create_batch(10, contact_name='Joe Shmoe')

        # records to be filtered out
        ContactRecordFactory.create_batch(10, contact_name='John Doe')

        # make sure end point is reachable
        response = self.client.post(reverse('search_records'),
                                    {'contact_name': 'Joe Shmoe',
                                     'output': 'json'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        # ensure a proper json response
        output = json.loads(response.content)
        self.assertIn('records', output)
        self.assertEqual(len(output['records']), 10)


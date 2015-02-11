"""Tests associated with the various MyReports views."""

# TODO:
#   * See about refactoring some of the repetitive parts of the filter_records
#     tests into the setUp method.
import json
from django.test import TestCase
from django.core.urlresolvers import reverse

from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import UserFactory
from mypartners.tests.factories import (ContactFactory, ContactRecordFactory,
                                        LocationFactory, PartnerFactory)
from seo.tests.factories import CompanyFactory, CompanyUserFactory


class MyReportsTestCase(TestCase):
    """
    Base class for all MyReports Tests. Identical to `django.test.TestCase`
    except that it provides a MyJobs TestClient instance and a logged in user.
    """
    def setUp(self):
        self.client = TestClient()
        self.user = UserFactory(email='testuser@directemployers.org',
                                is_staff=True)
        self.company = CompanyFactory(name='Test Company')
        self.partner = PartnerFactory(name='Test Partner', owner=self.company)

        # associate company to user
        CompanyUserFactory(user=self.user, company=self.company)

        self.client.login_user(self.user)


class TestReports(MyReportsTestCase):
    """Tests the reports view, which is the landing page for reports."""

    def test_unavailable_if_not_staff(self):
        """
        Until release, MyReports should not be accessible by users who aren't
        staff.
        """

        self.user.is_staff = False
        self.user.save()
        response = self.client.post(reverse('reports'))

        self.assertEqual(response.status_code, 404)

    def test_available_to_staff(self):
        """Should be available to staff users."""

        response = self.client.get(reverse('reports'))

        self.assertEqual(response.status_code, 200)


class TestFilterRecords(MyReportsTestCase):
    """
    Tests the `filter_records` view which is used to query various models.
    """

    def setUp(self):
        super(TestFilterRecords, self).setUp()

        ContactRecordFactory.create_batch(10, partner=self.partner,
                                          contact_name='Joe Shmoe')

    def test_restricted_to_ajax(self):
        """View should only be reachable through AJAX."""

        response = self.client.post(
            reverse('filter_records',
                    kwargs={'app': 'mypartners', 'model': 'partner'}))

        self.assertEqual(response.status_code, 404)

    def test_restricted_to_post(self):
        """GET requests should raise a 404."""

        response = self.client.get(
            reverse('filter_records',
                    kwargs={'app': 'mypartners', 'model': 'partner'}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 404)

    def test_json_output(self):
        """Test that filtering contact records through ajax works properly."""

        # records to be filtered out
        ContactRecordFactory.create_batch(10, contact_name='John Doe')

        response = self.client.post(
            reverse('filter_records',
                    kwargs={'app': 'mypartners', 'model': 'contactrecord'}),
            {'contact_name': 'Joe Shmoe'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output['records']), 10)

    def test_only_user_results_returned(self):
        """Results should only contain records user has access to."""

        # records not owned by user
        partner = PartnerFactory(name="Wrong Partner")
        ContactRecordFactory.create_batch(10, partner=partner)

        response = self.client.post(
            reverse('filter_records',
                    kwargs={'app': 'mypartners', 'model': 'contactrecord'}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output['records']), 10)

    def test_filtering_on_partner(self):
        """Test the ability to filter by partner."""

        # we already have one because of self.partner
        PartnerFactory.create_batch(9, name="Test Partner",
                                    owner=self.company)

        response = self.client.post(
            reverse('filter_records',
                    kwargs={'app': 'mypartners', 'model': 'partner'}),
            {'name': 'Test Partner'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = json.loads(response.content)

        # ContactRecordFactory creates 10 partners in setUp
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output['records']), 10)

    def test_list_query_params(self):
        """Test that query parameters that are lists are parsed correctly."""

        ContactFactory.create_batch(10, partner__owner=self.company)

        response = self.client.post(
            reverse('filter_records',
                    kwargs={'app': 'mypartners', 'model': 'partner'}),
            {'contact': range(1, 6)},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output['records']), 5)

    def test_filtering_on_contact(self):
        """Test the ability to filter by contact."""

        ContactFactory.create_batch(10, name="Jane Doe",
                                    partner=self.partner)

        # contacts with the wrong name
        ContactFactory.create_batch(10, name="Jane Smith",
                                    partner=self.partner)

        response = self.client.post(
            reverse('filter_records',
                    kwargs={'app': 'mypartners', 'model': 'contact'}),
            {'name': 'Jane Doe'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output['records']), 10)

    def test_filter_by_state(self):
        """Tests that filtering by state works."""

        indiana = LocationFactory(state="IN")
        ContactFactory.create_batch(10, name="Jane Doe", partner=self.partner, 
                                    locations=[indiana])

        response = self.client.post(
            reverse('filter_records',
                    kwargs={'app': 'mypartners', 'model': 'contact'}),
            {'state': 'IN'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = json.loads(response.content)
        
        self.assertEqual(len(output['records']), 10)

    def test_order_by(self):
        """Tests that `order_by` parameter is passed to `QuerySet`."""

        # mix up the order they are created in so that blanks aren't all next
        # to each other
        PartnerFactory.create_batch(10, owner=self.company, name="New Partner")
        PartnerFactory.create_batch(10, owner=self.company)

        response = self.client.post(
            reverse('filter_records',
                    kwargs={'app': 'mypartners', 'model': 'partner'}),
            {'order_by': 'name'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = json.loads(response.content)
        records = output['records']

        self.assertTrue(records[0]['name'] < records[-1]['name'])

    def test_cached_results(self):
        """
        Tests that hitting the view multiple times with the same parameters
        returns a cached result. Also tests that ignoring cache works properly.
        """
        ContactRecordFactory.create_batch(10, partner=self.partner)

        url = reverse('filter_records',
                      kwargs={'app': 'mypartners', 'model': 'contactrecord'})
        kwargs = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

        # this request should not be cached
        response = self.client.post(url, **kwargs)
        output = json.loads(response.content)
        self.assertFalse(output['cached'])

        # this call should be cached
        response = self.client.post(url, **kwargs)
        output = json.loads(response.content)
        self.assertTrue(output['cached'])

        # this call should not be cached as we ignore the cache
        response = self.client.post(url + '?ignore_cache', **kwargs)
        output = json.loads(response.content)
        self.assertFalse(output['cached'])

    def test_count_annotation(self):
        """
        When `count` is passed to the view, the resulting records should be
        annotated as a `Count` for the field passed to count.
        """

        response = self.client.post(
            reverse('filter_records',
                    kwargs={'app': 'mypartners', 'model': 'partner'}),
            {'count': 'contact'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(all('count' in record for record in output['records']))

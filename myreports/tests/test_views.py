"""Tests associated with the various MyReports views."""

# TODO: Remove custom manager specific tests to a separate test case.

import json
import unittest

from django.test import TestCase
from django.core.urlresolvers import reverse

from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import UserFactory
from mypartners.models import Partner
from mypartners.tests.factories import (ContactFactory, ContactRecordFactory,
                                        PartnerFactory)
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
        response = self.client.get(reverse('reports'))

        self.assertEqual(response.status_code, 404)

    def test_available_to_staff(self):
        """Should be available to staff users."""

        response = self.client.get(reverse('reports'))

        self.assertEqual(response.status_code, 200)


class TestSearchRecords(MyReportsTestCase):
    """
    Tests the `filter_records` view which is used to query various models.
    """

    def setUp(self):
        super(TestSearchRecords, self).setUp()

        ContactRecordFactory.create_batch(10, partner=self.partner,
                                          contact_name='Joe Shmoe')

    def test_restricted_to_ajax(self):
        """View should only be reachable through AJAX."""

        response = self.client.get(reverse('filter_partners'))

        self.assertEqual(response.status_code, 404)

    @unittest.skip("TODO: Change AJAX requests to GET")
    def test_restricted_to_get(self):
        """GET requests should raise a 404."""

        response = self.client.get(reverse('filter_partners'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 404)

    def test_json_output(self):
        """Test that filtering contact records through ajax works properly."""

        # records to be filtered out
        ContactRecordFactory.create_batch(10, contact_name='John Doe')

        response = self.client.get(reverse('filter_records',
                                   kwargs={'model': 'ContactRecord'}),
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

        response = self.client.get(reverse('filter_records',
                                   kwargs={'model': 'ContactRecord'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output['records']), 10)

    def test_filtering_on_partner(self):
        """Test the ability to filter by partner."""

        # we already have one because of self.partner
        PartnerFactory.create_batch(9, name="Test Partner",
                                    owner=self.company)

        response = self.client.get(reverse('filter_partners'),
                                   {'name': 'Test Partner'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = response.context

        # ContactRecordFactory creates 10 partners in setUp
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output['records']), 10)

    def test_list_query_params(self):
        """Test that query parameters that are lists are parsed correctly."""

        ContactFactory.create_batch(10, partner__owner=self.company)

        response = self.client.get(reverse('filter_partners'),
                                   {'contact': range(1, 6)},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = response.context

        self.assertEqual(response.status_code, 200)
        self.assertEqual(output['records'].count(), 5)

    def test_filtering_on_contact(self):
        """Test the ability to filter by contact."""

        ContactFactory.create_batch(10, name="Jane Doe",
                                    partner=self.partner)

        # contacts with the wrong name
        ContactFactory.create_batch(10, name="Jane Smith",
                                    partner=self.partner)

        response = self.client.get(reverse('filter_contacts'),
                                   {'name': 'Jane Doe'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        output = response.context

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output['records']), 10)

    def test_sort_by_order(self):
        """Tests that `sort_order` orders blank values after others."""

        PartnerFactory.create_batch(10)
        PartnerFactory.create_batch(10, name="")

        partners = list(Partner.objects.sort_by('name'))

        self.assertEqual(partners[0].name, "Company")
        self.assertEqual(partners[-1].name, "")

"""Tests associated with the various MyReports views."""

import json

from django.test import TestCase
from django.core.urlresolvers import reverse

from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import UserFactory
from mypartners.tests.factories import (ContactFactory, ContactRecordFactory,
                                        LocationFactory, PartnerFactory)
from myreports.models import Report
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


class TestOverview(MyReportsTestCase):
    """Tests the reports view, which is the landing page for reports."""

    def test_unavailable_if_not_staff(self):
        """
        Until release, MyReports should not be accessible by users who aren't
        staff.
        """

        self.user.is_staff = False
        self.user.save()
        response = self.client.post(reverse('overview'))

        self.assertEqual(response.status_code, 404)

    def test_available_to_staff(self):
        """Should be available to staff users."""

        response = self.client.get(reverse('overview'))

        self.assertEqual(response.status_code, 200)


class TestViewRecords(MyReportsTestCase):
    """
    Tests the `view_records` view which is used to query various models.
    """

    def setUp(self):
        super(TestViewRecords, self).setUp()
        self.client = TestClient(path='/reports/ajax/mypartners',
                                 HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.client.login_user(self.user)

        ContactRecordFactory.create_batch(
            10, partner=self.partner, contact_name='Joe Shmoe')

    def test_restricted_to_ajax(self):
        """View should only be reachable through AJAX."""

        self.client.path += '/partner'
        self.client.defaults.pop('HTTP_X_REQUESTED_WITH')
        response = self.client.post()

        self.assertEqual(response.status_code, 404)

    def test_restricted_to_get(self):
        """POST requests should raise a 404."""

        self.client.path += '/partner'
        response = self.client.post()

        self.assertEqual(response.status_code, 404)

    def test_json_output(self):
        """Test that filtering contact records through ajax works properly."""

        # records to be filtered out
        ContactRecordFactory.create_batch(10, contact_name='John Doe')

        self.client.path += '/contactrecord'
        response = self.client.get(data={'contact_name': 'Joe Shmoe'})
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output), 10)

    def test_only_user_results_returned(self):
        """Results should only contain records user has access to."""

        # records not owned by user
        partner = PartnerFactory(name="Wrong Partner")
        ContactRecordFactory.create_batch(10, partner=partner)

        self.client.path += '/contactrecord'
        response = self.client.get()
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output), 10)

    def test_filtering_on_partner(self):
        """Test the ability to filter by partner."""

        # we already have one because of self.partner
        PartnerFactory.create_batch(9, name="Test Partner", owner=self.company)

        self.client.path += '/partner'
        response = self.client.get(data={'name': 'Test Partner'})
        output = json.loads(response.content)

        # ContactRecordFactory creates 10 partners in setUp
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output), 10)

    def test_list_query_params(self):
        """Test that query parameters that are lists are parsed correctly."""

        contacts = ContactFactory.create_batch(10, partner__owner=self.company)
        pks = [contact.pk for contact in contacts[:5]]

        self.client.path += '/partner'
        response = self.client.get(data={'contact': pks})
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output), 5)

    def test_filtering_on_contact(self):
        """Test the ability to filter by contact."""

        ContactFactory.create_batch(10, name="Jen Doe", partner=self.partner)

        # contacts with the wrong name
        ContactFactory.create_batch(10, name="Jen Smith", partner=self.partner)

        self.client.path += '/contact'
        response = self.client.get(data={'name': 'Jen Doe'})
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(output), 10)

    def test_filter_by_state(self):
        """Tests that filtering by state works."""

        indiana = LocationFactory(state="IN")
        ContactFactory.create_batch(10, name="Jen Doe", partner=self.partner,
                                    locations=[indiana])

        self.client.path += '/contact'
        response = self.client.get(data={'state': 'IN'})
        output = json.loads(response.content)

        self.assertEqual(len(output), 10)

    def test_filter_by_city(self):
        """Tests that filtering by city works."""

        indianapolis = LocationFactory(city="Indianapolis")
        ContactFactory.create_batch(10, name="Jen Doe", partner=self.partner,
                                    locations=[indianapolis])

        self.client.path += '/contact'
        response = self.client.get(data={'city': 'indianapolis'})
        output = json.loads(response.content)

        self.assertEqual(len(output), 10)

    def test_counts(self):
        """
        When `count` is passed to the view, the resulting records should be
        annotated as a `Count` for the field passed to count.
        """

        self.client.path += '/partner'
        response = self.client.get(data={'count': 'contact'})
        output = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(all('count' in record for record in output))


class TestReportView(MyReportsTestCase):
    """
    Tests the ReportView class, which is used to create and retrieve
    reports.
    """
    def setUp(self):
        super(TestReportView, self).setUp()
        self.client = TestClient(path='/reports/view/mypartners/contactrecord')
        self.client.login_user(self.user)

        ContactRecordFactory.create_batch(5, partner__owner=self.company)
        ContactRecordFactory.create_batch(
            5, contact_type='job', job_applications=1,
            partner__owner=self.company)
        ContactRecordFactory.create_batch(
            5, contact_type='job',
            job_hires=1, partner__owner=self.company)

    def test_create_report(self):
        """Test that a report model instance is properly created."""

        # create a report whose results is for all contact records in the
        # company
        response = self.client.post()
        report_name = response.content
        report = Report.objects.get(name=report_name)

        self.assertEqual(len(report.python), 15)

        # we use this in other tests

        return report_name

    def test_get_report(self):
        """Test that chart data is retreived from record results."""

        report_name = self.test_create_report()
        report = Report.objects.get(name=report_name)

        response = self.client.get(data={'id': report.pk})
        data = json.loads(response.content)

        # check contact record stats
        for key in ['applications', 'hires', 'communications', 'emails']:
            self.assertEqual(data[key], 5)

        # check contact stats
        self.assertEqual(data['contacts'][0]['records'], 5)
        self.assertEqual(data['contacts'][0]['referrals'], 10)

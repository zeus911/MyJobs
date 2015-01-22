"""Tests associated with the various MyReports views."""

from django.test import TestCase
from django.core.urlresolvers import reverse

from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import UserFactory

class TestReportsOverview(TestCase):
    """Tests the reports_overview view."""

    def setUp(self):
        self.client = TestClient()
        # TODO: on release of MyReports, change this to set more appropriate
        #       permissions
        self.user = UserFactory(email="testuser@directemployers.org",
                                is_staff=True)
        self.client.login_user(self.user)

    def test_access_restricted_to_staff(self):
        """Until release, MyReports should only be viewable by staff users."""

        response = self.client.get(reverse('reports_overview'))

        self.assertRedirects(response, "{}?next={}".format(
            reverse('home'), reverse('reports_overview')))


class TestEditReport(TestCase):
    """
    Tests the edit_report view, which implements both editing and viewing of
    reports.
    """
    pass

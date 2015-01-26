"""Tests associated with the various MyReports views."""

from django.test import TestCase
from django.core.urlresolvers import reverse

from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import UserFactory

class TestReports(TestCase):
    """Tests the reports view, which is the landing page for reports"""

    def setUp(self):
        self.client = TestClient()
        # TODO: on release of MyReports, change this to set more appropriate
        #       permissions
        self.user = UserFactory(email="testuser@directemployers.org",
                                is_staff=True)
        self.client.login_user(self.user)

    def test_access_restricted_to_staff(self):
        """Until release, MyReports should only be viewable by staff users."""

        self.user.is_staff = False
        self.user.save()
        response = self.client.get(reverse('reports'))

        self.assertEqual(response.status_code, 404)

    def test_filter_partners(self):
        """Test that filtering partners through ajax works properly."""
        import ipdb; ipdb.set_trace()
        response = self.client.post(reverse('reports'),
                                    {'name': 'DirectEmployers'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

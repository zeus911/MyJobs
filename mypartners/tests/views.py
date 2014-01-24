from bs4 import BeautifulSoup
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from myjobs.tests.views import TestClient
from myjobs.tests.factories import UserFactory
from mydashboard.models import CompanyUser
from mydashboard.tests.factories import CompanyFactory, CompanyUserFactory
from mypartners.tests.factories import PartnerFactory, ContactFactory
from mypartners.models import Partner, Contact


class MyPartnerViewsTests(TestCase):
    def setUp(self):
        super(MyPartnerViewsTests, self).setUp()
        self.staff_user = UserFactory()
        group = Group.objects.get(name=CompanyUser.GROUP_NAME)
        self.staff_user.groups.add(group)
        self.staff_user.save()

        self.company = CompanyFactory()
        self.company.save()
        self.admin = CompanyUserFactory(user=self.staff_user,
                                        company=self.company)
        self.client = TestClient()
        self.client.login_user(self.user)

        self.partner = PartnerFactory(owner=self.company)
        self.contact = ContactFactory()

    def test_prm_page(self):
        response = self.client.post(reverse('prm') +
                                    '?company='+str(self.company.id))
        self.assertEqual(response.status_code, 200)
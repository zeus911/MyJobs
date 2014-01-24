from bs4 import BeautifulSoup
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from myjobs.tests.views import TestClient
from myjobs.tests.factories import UserFactory
from mydashboard.models import CompanyUser
from mydashboard.tests.factories import CompanyFactory, CompanyUserFactory
from mypartners.tests.factories import PartnerFactory, ContactFactory


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
        self.client.login_user(self.staff_user)

        self.partner = PartnerFactory(owner=self.company)
        self.contact = ContactFactory()
        self.contact.save()
        self.partner.add_contact(self.contact)
        self.partner.save()

    def test_prm_page_with_no_partners(self):
        """
        Tests the prm page with no partners. Also tests users that input
        /prm/view as a URL
        """
        self.partner.delete()
        response = self.client.post('/prm/view')
        soup = BeautifulSoup(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(soup.select('small')[0].contents[0], 'Test Company')

        response = self.client.post(reverse('prm') +
                                    '?company='+str(self.company.id))
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        # blanket is the class that holds the fake table on prm view when
        # there are no partners
        self.assertEqual(len(soup.select('.blanket')), 1)

    def test_prm_page_with_a_partner(self):
        response = self.client.post('/prm/view')
        soup = BeautifulSoup(response.content)

        # 1 tr is dedicated to header, 1 tr for partner.
        self.assertEqual(len(soup.select('tr')), 2)

        x = 0
        while x < 8:
            partner = PartnerFactory(owner=self.company)
            partner.save()
            x += 1

        response = self.client.post('/prm/view')
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select('tr')), 10)

    def test_partner_details_with_no_contacts(self):
        self.contact.delete()
        response = self.client.post(reverse('partner_details') +
                                    '?company='+str(self.company.id) +
                                    '&partner='+str(self.partner.id))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertFalse(soup.select('table'))

    def test_partner_details_with_contacts(self):
        response = self.client.post(reverse('partner_details') +
                                    '?company='+str(self.company.id) +
                                    '&partner='+str(self.partner.id))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertTrue(soup.select('table'))

        x = 0
        while x < 9:
            contact = ContactFactory()
            contact.save()
            self.partner.add_contact(contact)
            x += 1
        self.partner.save()

        response = self.client.post(reverse('partner_details') +
                                    '?company='+str(self.company.id) +
                                    '&partner='+str(self.partner.id))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertEqual(len(soup.select('tr')), 10)

from bs4 import BeautifulSoup
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from myjobs.tests.views import TestClient
from myjobs.tests.factories import UserFactory
from mydashboard.models import CompanyUser
from mydashboard.tests.factories import CompanyFactory, CompanyUserFactory
from mypartners.tests.factories import (PartnerFactory, ContactFactory,
                                        ContactLogEntryFactory,
                                        ContactRecordFactory)
from mysearches.tests.factories import PartnerSavedSearchFactory
from django.contrib.localflavor import be
from datetime import datetime


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
                                    '?company=' + str(self.company.id))
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

        for _ in range(8):
            partner = PartnerFactory(owner=self.company)
            partner.save()

        response = self.client.post('/prm/view')
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select('tr')), 10)

    def test_partner_details_with_no_contacts(self):
        self.contact.delete()
        response = self.client.post(reverse('partner_details') +
                                    '?company=' + str(self.company.id) +
                                    '&partner=' + str(self.partner.id))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertFalse(soup.select('table'))

    def test_partner_details_with_contacts(self):
        response = self.client.post(reverse('partner_details') +
                                    '?company=' + str(self.company.id) +
                                    '&partner=' + str(self.partner.id))
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
                                    '?company=' + str(self.company.id) +
                                    '&partner=' + str(self.partner.id))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertEqual(len(soup.select('tr')), 10)


class PartnerOverviewTests(TestCase):
    def setUp(self):
        super(PartnerOverviewTests, self).setUp()

        # Create a user to login as
        self.staff_user = UserFactory()
        group = Group.objects.get(name=CompanyUser.GROUP_NAME)
        self.staff_user.groups.add(group)
        self.staff_user.save()

        # Create a company
        self.company = CompanyFactory()
        self.company.save()
        self.admin = CompanyUserFactory(user=self.staff_user,
                                        company=self.company)

        # Create a partner
        self.partner = PartnerFactory(owner=self.company)
        self.primary_contact = ContactFactory(name="Example Name")
        self.primary_contact.save()
        self.partner.primary_contact = self.primary_contact
        self.partner.save()

        # Create a contact
        self.contact = ContactFactory()
        self.contact.save()

        # Create a TestClient
        self.client = TestClient()
        self.client.login_user(self.staff_user)

    def get_url(self, **kwargs):
        args = ["%s=%s" % (k, v) for k, v in kwargs.items()]
        args = '&'.join(args)
        return reverse('partner_overview') + '?' + args

    def test_organization_details(self):
        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)

        # Assert we return a 200 response.
        self.assertEqual(response.status_code, 200)

        # Assert details about the Organization Infobox
        soup = BeautifulSoup(response.content)
        container = soup.find(id='partner-details')

        self.assertIn(self.partner.name, container.get_text())
        self.assertIn(self.primary_contact.name, container.get_text())
        self.assertIn(self.primary_contact.email, container.get_text())

    def test_no_recent_activity(self):

        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)

        # Assert we return a 200 response.
        self.assertEqual(response.status_code, 200)

        # Assert details about the Organization Infobox
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-activity')
        self.assertEqual(len(container('tr')), 0)

    def test_recent_activity(self):
        # Add recent activity
        user = UserFactory(email="temp@user.com")
        for i in range(1, 4):
            ContactLogEntryFactory(partner=self.partner, action_flag=i,
                                   user=user)

        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)

        # Assert we return a 200 response.
        self.assertEqual(response.status_code, 200)

        # Assert details about the Organization Infobox
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-activity')
        self.assertEqual(len(container('tr')), 3)

        # Assert the correct messages were displayed
        delete_msg = "deleted a contact for Example Contact Log"
        self.assertIn(delete_msg, container('tr')[0].get_text())
        update_msg = "updated a contact for Example Contact Log"
        self.assertIn(update_msg, container('tr')[1].get_text())
        add_msg = "added a contact for Example Contact Log"
        self.assertIn(add_msg, container('tr')[2].get_text())

        # Test that only a maximum of 10 records are displayed.
        for _ in range(12):
            ContactLogEntryFactory(partner=self.partner,
                                   user=user)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-activity')
        self.assertEqual(len(container('tr')), 10)

    def test_no_recent_communication_records(self):
        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)

        # Assert details about the Organization Infobox
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-communications-records')
        # Include 1 header row
        self.assertEqual(len(container('tr')), 2)
        no_records_msg = "No Recent Communication Records"
        self.assertIn(no_records_msg, container('tr')[1].get_text())

    def test_recent_communication_records(self):
        for _ in range(2):
            ContactRecordFactory(partner=self.partner)

        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)

        # Assert details about the Organization Infobox
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-communications-records')
        # Include 1 header row
        self.assertEqual(len(container('tr')), 3)

        contact_msg = "An employee emailed example@email.com"
        for row in container('tr')[1:]:
            self.assertIn(contact_msg, row.get_text())
            self.assertIn('Test Subject', row.get_text())

        # Test that only a maximum of 3 records are displayed.
        for _ in range(4):
            ContactRecordFactory(partner=self.partner)

        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-communications-records')
        self.assertEqual(len(container('tr')), 4)

    def test_no_recent_saved_searches(self):
        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)

        # Assert details about the Organization Infobox
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-saved-searches')
        # Include 1 header row
        self.assertEqual(len(container('tr')), 2)
        no_records_msg = "No Recent Saved Searches"
        self.assertIn(no_records_msg, container('tr')[1].get_text())

    def test_recent_saved_searches(self):
        user = UserFactory(email="alice@email.com")
        self.contact.user = user
        self.contact.save()

        self.partner.add_contact(self.contact)
        for _ in range(2):
            PartnerSavedSearchFactory(user=self.contact.user,
                                      provider=self.company,
                                      created_by=self.staff_user)

        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-saved-searches')

        # Include 1 header row
        self.assertEqual(len(container('tr')), 3)
        for row in container('tr')[1:]:
            self.assertIn("All Jobs", row('td')[0].get_text())
            self.assertIn("http://www.my.jobs/jobs", row('td')[1].get_text())

        # Test that only a maximum of 3 records are displayed.
        for _ in range(4):
            PartnerSavedSearchFactory(user=self.contact.user,
                                      provider=self.company,
                                      created_by=self.staff_user)

        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-saved-searches')
        self.assertEqual(len(container('tr')), 4)


class RecordViewTests(TestCase):
    def setUp(self):
        super(RecordViewTests, self).setUp()

        # Create a user to login as
        self.staff_user = UserFactory()
        group = Group.objects.get(name=CompanyUser.GROUP_NAME)
        self.staff_user.groups.add(group)
        self.staff_user.save()

        # Create a company
        self.company = CompanyFactory()
        self.company.save()
        self.admin = CompanyUserFactory(user=self.staff_user,
                                        company=self.company)

        # Create a partner
        self.partner = PartnerFactory(owner=self.company)
        self.primary_contact = ContactFactory(name="Example Name")
        self.primary_contact.save()
        self.partner.primary_contact = self.primary_contact
        self.partner.save()

        # Create a contact
        self.contact = ContactFactory()
        self.contact.user = UserFactory(email="test@test.com")
        self.contact.save()

        # Create a ContactRecord
        self.contact_record = ContactRecordFactory(partner=self.partner)
        self.dt = datetime(year=2014, month=3, day=4)
        self.contact_log_entery = ContactLogEntryFactory(partner=self.partner,
                                     user=self.contact.user,
                                     action_time=self.dt,
                                     object_id=self.contact_record.id)

        # Create a TestClient
        self.client = TestClient()
        self.client.login_user(self.staff_user)

    def get_url(self, **kwargs):
        args = ["%s=%s" % (k, v) for k, v in kwargs.items()]
        args = '&'.join(args)
        return reverse('record_view') + '?' + args

    def test_contact_details(self):
        url = self.get_url(partner=self.partner.id,
                           company=self.company.id,
                           id=self.contact_record.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Assert details of content on page
        soup = BeautifulSoup(response.content)
        details = soup.find(id="details")
        self.assertIn('example-contact', details.get_text())
        self.assertIn('example@email.com', details.get_text())
        self.assertIn('Test Subject', soup.find(id="subject").get_text())
        self.assertIn('Email', soup.find(id="type").get_text())
        self.assertIn('Some notes go here.', soup.find(id="notes").get_text())
        self.assertIn('Added - Mar 04, 2014',
                      soup.find(id="record-history").get_text())




    def test_record_history(self):
        url = self.get_url(partner=self.partner.id,
                           company=self.company.id,
                           id=self.contact_record.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        self.assertIn('Added - Mar 04, 2014',
                      soup.find(id="record-history").get_text())

        # Add more events
        for i in range(2, 4):
            ContactLogEntryFactory(partner=self.partner, action_flag=i,
                                     user=self.contact.user,
                                     action_time=self.dt,
                                     object_id=self.contact_record.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)

        history = soup.find(id='record-history').get_text()
        for text in ['Added - Mar 04, 2014',
                  'Updated - Mar 04, 2014',
                  'Deleted - Mar 04, 2014']:
            self.assertIn(text, history)

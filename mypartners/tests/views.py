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
from datetime import datetime, timedelta
from mypartners.models import ContactRecord


class MyPartnerViewsTests(TestCase):
    """Tests for the /prm/view/ page"""
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
    """Tests related to the partner overview page, /prm/view/overview/"""
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


class RecordsOverviewTests(TestCase):
    """Tests related to the records overview page, /prm/view/records/"""

    def setUp(self):
        super(RecordsOverviewTests, self).setUp()

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

        # Create a TestClient
        self.client = TestClient()
        self.client.login_user(self.staff_user)

    def get_url(self, **kwargs):
        args = ["%s=%s" % (k, v) for k, v in kwargs.items()]
        args = '&'.join(args)
        return reverse('partner_records') + '?' + args

    def test_no_contact_records(self):
        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        soup = soup.find(id='view-records')
        self.assertIn('No records available.', soup.get_text())

    def test_records_counts(self):
        for _ in range(5):
            ContactRecordFactory(partner=self.partner)

        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        records = soup.find(id='view-records')
        self.assertEqual(len(records('tr')), 6)

        # Ensure old records don't show
        ContactRecordFactory(partner=self.partner,
                             date_time=datetime.now() - timedelta(days=31))
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        records = soup.find(id='view-records')
        self.assertEqual(len(records('tr')), 6)

    def test_most_recent_activity(self):
        raise NotImplementedError()


class RecordsDetailsTests(TestCase):
    """Tests related to the records detail page, /prm/view/records/view/"""
    def setUp(self):
        super(RecordsDetailsTests, self).setUp()

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
        self.contact_log_entry = ContactLogEntryFactory(partner=self.partner,
                                     user=self.contact.user,
                                     object_id=self.contact_record.id)
        self.contact_log_entry.save()

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
        self.assertEqual(len(soup.find(id="record-history")('br')), 1,
                         msg=soup.find(id="record-history"))

    def test_record_history(self):
        url = self.get_url(partner=self.partner.id,
                           company=self.company.id,
                           id=self.contact_record.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.find(id="record-history")('br')), 1,
                         msg=soup.find(id="record-history"))

        # Add more events
        for i in range(2, 4):
            ContactLogEntryFactory(partner=self.partner, action_flag=i,
                                     user=self.contact.user,
                                     object_id=self.contact_record.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)

        self.assertEqual(len(soup.find(id='record-history')('br')), 3)


class RecordsEditTests(TestCase):
    """Tests related to the record edit page, /prm/view/records/edit"""
    def setUp(self):
        super(RecordsEditTests, self).setUp()

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

        # Create a contact
        self.primary_contact = ContactFactory(name="Example Name")
        self.primary_contact.save()

        self.contact = ContactFactory()
        self.contact.user = UserFactory(email="test@test.com")
        self.contact.save()

        # Create a partner
        self.partner = PartnerFactory(owner=self.company)
        self.partner.primary_contact = self.primary_contact
        self.partner.add_contact(self.contact)
        self.partner.save()

        # Create a ContactRecord
        self.contact_record = ContactRecordFactory(partner=self.partner,
                                   contact_name=self.contact.name)
        self.contact_log_entry = ContactLogEntryFactory(partner=self.partner,
                                     user=self.contact.user,
                                     object_id=self.contact_record.id)
        self.contact_log_entry.save()

        # Create a TestClient
        self.client = TestClient()
        self.client.login_user(self.staff_user)

    def get_url(self, **kwargs):
        args = ["%s=%s" % (k, v) for k, v in kwargs.items()]
        args = '&'.join(args)
        return reverse('partner_edit_record') + '?' + args

    def test_render_new_form(self):
        url = self.get_url(partner=self.partner.id,
                           company=self.company.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        form = soup.find('fieldset')

        self.assertEqual(len(form(class_='profile-form-input')), 14)
        self.assertEqual(len(form.find(id='id_contact_name')('option')), 2)

        # Add contact
        contact = ContactFactory()
        contact.user = UserFactory(email="test-2@test.com")
        contact.save()
        self.partner.add_contact(contact)
        self.partner.save()

        # Test form is updated with new contact
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        form = soup.find(id='id_contact_name')
        self.assertEqual(len(form('option')), 3)

    def test_render_existing_data(self):
        url = self.get_url(partner=self.partner.id,
                           company=self.company.id,
                           id=self.contact_record.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        form = soup.find('fieldset')

        self.assertEqual(len(form(class_='profile-form-input')), 14)
        self.assertEqual(len(form.find(id='id_contact_name')('option')), 1)

        contact_type = form.find(id='id_contact_type')
        contact_type = contact_type.find(selected='selected').get_text()
        self.assertEqual(contact_type, 'Email')

        self.assertIn(self.contact.name,
                      form.find(id='id_contact_name').get_text())
        self.assertIn('example@email.com',
                      form.find(id='id_contact_email')['value'])
        self.assertIn(self.contact_record.subject,
                      form.find(id='id_subject')['value'])

        # Test dates
        self.assertIn("Jan", form.find(id='id_date_time_0').get_text())
        self.assertIn("01", form.find(id='id_date_time_1').get_text())
        self.assertIn("2014", form.find(id='id_date_time_2').get_text())
        self.assertIn("05", form.find(id='id_date_time_3').get_text())
        self.assertIn("00", form.find(id='id_date_time_4').get_text())
        self.assertIn("AM", form.find(id='id_date_time_5').get_text())

        self.assertIn(self.contact_record.notes,
                      form.find(id='id_notes').get_text())

    def test_create_new_contact_record(self):

        url = self.get_url(partner=self.partner.id,
                           company=self.company.id)

        data = {'contact_type': 'email',
                'contact_name': self.contact.id,
                'contact_email': 'test@email.com',
                'contact_phone': '',
                'location': '',
                'length_0': '00',
                'length_1': '00',
                'subject': '',
                'date_time_0': 'Jan',
                'date_time_1': '01',
                'date_time_2': '2005',
                'date_time_3': '01',
                'date_time_4': '00',
                'date_time_5': 'AM',
                'job_id': '',
                'job_applications': '',
                'job_interviews': '',
                'job_hires': '',
                'notes': 'A few notes here',
                'company': self.company.id,
                'partner': self.partner.id}
        response = self.client.post(url, data=data)
        soup = BeautifulSoup(response.content)
        self.assertEqual(response.status_code, 302)

        record = ContactRecord.objects.get(contact_email='test@email.com')
        self.assertEqual(record.partner, self.partner)
        self.assertEqual(record.contact_type, 'email')
        self.assertEqual(record.contact_email, data['contact_email'])
        self.assertEqual(record.notes, data['notes'])

    def test_update_existing_contact_record(self):
        url = self.get_url(partner=self.partner.id,
                           company=self.company.id,
                           id=self.contact_record.id)

        data = {'contact_type': 'email',
                'contact_name': self.contact.id,
                'contact_email': 'test@email.com',
                'contact_phone': '',
                'location': '',
                'length_0': '00',
                'length_1': '00',
                'subject': '',
                'date_time_0': 'Jan',
                'date_time_1': '01',
                'date_time_2': '2005',
                'date_time_3': '01',
                'date_time_4': '00',
                'date_time_5': 'AM',
                'job_id': '',
                'job_applications': '',
                'job_interviews': '',
                'job_hires': '',
                'notes': 'A few notes here',
                'company': self.company.id,
                'partner': self.partner.id}
        response = self.client.post(url, data=data)
        soup = BeautifulSoup(response.content)
        self.assertEqual(response.status_code, 302)

        # Get an updated copy of the ContactRecord
        record = ContactRecord.objects.get(id=self.contact_record.id)
        self.assertEqual(record.partner, self.partner)
        self.assertEqual(record.contact_type, 'email')
        self.assertEqual(record.contact_email, data['contact_email'])
        self.assertEqual(record.notes, data['notes'])


class SearchesOverviewTests(TestCase):
    """Tests related to the search overview page, /prm/view/searches"""

    def test_no_searches(self):
        raise NotImplementedError()

    def test_render_search_list(self):
        raise NotImplementedError()


class SearchFeedTests(TestCase):
    """Tests relating to the search feed page, /prm/view/searches/feed"""

    def test_details(self):
        raise NotImplementedError()

    def test_feed_results(self):
        raise NotImplementedError()


class SearchEditTests(TestCase):
    """Tests relating to the edit search page /prm/view/searches/edit"""

    def test_render_new_form(self):
        raise NotImplementedError()

    def test_render_existing_data(self):
        raise NotImplementedError()

    def test_render_error_conditions(self):
        raise NotImplementedError()

    def test_create_new_contact_record(self):
        raise NotImplementedError()

    def test_update_existing_contact_record(self):
        raise NotImplementedError()

from bs4 import BeautifulSoup
import json
import re
from time import sleep

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core import mail
from django.utils.timezone import utc

from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import UserFactory
from mydashboard.models import CompanyUser
from mydashboard.tests.factories import CompanyFactory, CompanyUserFactory
from mypartners.tests.factories import (PartnerFactory, ContactFactory,
                                        ContactLogEntryFactory,
                                        ContactRecordFactory)
from mysearches.tests.factories import PartnerSavedSearchFactory
from datetime import datetime, timedelta
from mypartners.models import Contact, ContactRecord, ContactLogEntry, ADDITION
from mypartners.helpers import find_partner_from_email
from mysearches.models import PartnerSavedSearch


class MyPartnersTestCase(TestCase):
    def setUp(self):
        super(MyPartnersTestCase, self).setUp()

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
        self.client = TestClient()
        self.client.login_user(self.staff_user)

        # Create a partner
        self.partner = PartnerFactory(owner=self.company, pk=1)

        # Create a contact
        self.contact = ContactFactory(partner=self.partner,
                                      user=UserFactory(email="contact@user.com"),
                                      email="contact@user.com")

        # Create a TestClient
        self.client = TestClient()
        self.client.login_user(self.staff_user)

    def get_url(self, view=None, **kwargs):
        if view == None:
            view = self.default_view
        args = ["%s=%s" % (k, v) for k, v in kwargs.items()]
        args = '&'.join(args)
        return reverse(view) + '?' + args


class MyPartnerViewsTests(MyPartnersTestCase):
    """Tests for the /prm/view/ page"""
    def setUp(self):
        super(MyPartnerViewsTests, self).setUp()

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
            contact = ContactFactory(partner=self.partner)
            x += 1

        response = self.client.post(reverse('partner_details') +
                                    '?company=' + str(self.company.id) +
                                    '&partner=' + str(self.partner.id))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertEqual(len(soup.select('tr')), 10)


class PartnerOverviewTests(MyPartnersTestCase):
    """Tests related to the partner overview page, /prm/view/overview/"""
    def setUp(self):
        super(PartnerOverviewTests, self).setUp()

        self.default_view = 'partner_overview'

        # Create a primary contact
        self.primary_contact = ContactFactory(name="Example Name",
                                              partner=self.partner)
        self.primary_contact.save()

        self.partner.primary_contact = self.primary_contact
        self.partner.save()

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
            sleep(1)

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
            contact_record = ContactRecordFactory(partner=self.partner)
            ContactLogEntryFactory(partner=self.partner,
                                   user=None,
                                   object_id=contact_record.id)

        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)

        # Assert details about the Organization Infobox
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-communications-records')
        # Include 1 header row
        self.assertEqual(len(container('tr')), 3)

        contact_msg = "Email\nexample-contact\nTest Subject\nSome notes go here.\n"
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

        for _ in range(2):
            PartnerSavedSearchFactory(user=self.contact.user,
                                      provider=self.company,
                                      created_by=self.staff_user,
                                      partner=self.partner)

        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-saved-searches')

        # Include 1 header row
        self.assertEqual(len(container('tr')), 3)
        for row in container('tr')[1:]:
            self.assertIn("All Jobs", row('td')[0].get_text())
            self.assertIn("alice@example.com", row('td')[1].get_text())

        # Test that only a maximum of 3 records are displayed.
        for _ in range(4):
            PartnerSavedSearchFactory(user=self.contact.user,
                                      provider=self.company,
                                      created_by=self.staff_user,
                                      partner=self.partner)

        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-saved-searches')
        self.assertEqual(len(container('tr')), 4)


class RecordsOverviewTests(MyPartnersTestCase):
    """Tests related to the records overview page, /prm/view/records/"""

    def setUp(self):
        super(RecordsOverviewTests, self).setUp()

        self.default_view = 'partner_records'

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


class RecordsDetailsTests(MyPartnersTestCase):
    """Tests related to the records detail page, /prm/view/records/view/"""
    def setUp(self):
        super(RecordsDetailsTests, self).setUp()

        self.default_view = 'record_view'

        # Create a ContactRecord
        self.contact_record = ContactRecordFactory(partner=self.partner)
        self.contact_log_entry = ContactLogEntryFactory(
            partner=self.partner, user=self.contact.user,
            object_id=self.contact_record.id,
            content_type=ContentType.objects.get_for_model(ContactRecord))
        self.contact_log_entry.save()

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
            ContactLogEntryFactory(
                partner=self.partner, action_flag=i, user=self.contact.user,
                object_id=self.contact_record.id,
                content_type=ContentType.objects.get_for_model(ContactRecord))
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)

        self.assertEqual(len(soup.find(id='record-history')('br')), 3)

    def test_export_special_chars(self):
        self.default_view = 'prm_export'

        ContactRecordFactory(notes='\u2019', partner=self.partner)

        url = self.get_url(partner=self.partner.id,
                           company=self.company.id,
                           id=self.contact_record.id,
                           file_format='csv')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_bleaching(self):
        """
        Makes sure html tags are correctly being stripped from the notes
        section.

        """
        notes = '<script>alert("test!");</script>'
        record = ContactRecordFactory(notes=notes, partner=self.partner)
        url = self.get_url(partner=self.partner.id,
                           company=self.company.id,
                           id=record.id)
        response = self.client.get(url)
        self.assertNotIn(notes, response.content)
        self.assertIn('alert("test!");', response.content)


class RecordsEditTests(MyPartnersTestCase):
    """Tests related to the record edit page, /prm/view/records/edit"""
    def setUp(self):
        super(RecordsEditTests, self).setUp()


        self.default_view = 'partner_edit_record'

        # Create a primary contact
        self.primary_contact = ContactFactory(name="Example Name",
                                              partner=self.partner)
        self.primary_contact.save()

        self.partner.primary_contact = self.primary_contact
        self.partner.save()

        # Create a ContactRecord
        self.contact_record = ContactRecordFactory(partner=self.partner,
                                     contact_name=self.contact.name)
        self.contact_log_entry = ContactLogEntryFactory(partner=self.partner,
                                     user=self.contact.user,
                                     object_id=self.contact_record.id)
        self.contact_log_entry.save()

    def test_render_new_form(self):
        url = self.get_url(partner=self.partner.id,
                           company=self.company.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        form = soup.find('fieldset')

        self.assertEqual(len(form(class_='profile-form-input')), 14)
        self.assertEqual(len(form.find(id='id_contact_name')('option')), 3)

        # Add contact
        ContactFactory(partner=self.partner,
                       user=UserFactory(email="test-2@test.com"))

        # Test form is updated with new contact
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        form = soup.find(id='id_contact_name')
        self.assertEqual(len(form('option')), 4)

    def test_render_existing_data(self):
        url = self.get_url(partner=self.partner.id,
                           company=self.company.id,
                           id=self.contact_record.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        form = soup.find('fieldset')

        self.assertEqual(len(form(class_='profile-form-input')), 14)
        self.assertEqual(len(form.find(id='id_contact_name')('option')), 2)

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
        self.assertEqual(response.status_code, 302)

        # Get an updated copy of the ContactRecord
        record = ContactRecord.objects.get(id=self.contact_record.id)
        self.assertEqual(record.partner, self.partner)
        self.assertEqual(record.contact_type, 'email')
        self.assertEqual(record.contact_email, data['contact_email'])
        self.assertEqual(record.notes, data['notes'])


class SearchesOverviewTests(MyPartnersTestCase):
    """Tests related to the search overview page, /prm/view/searches"""
    def setUp(self):
        super(SearchesOverviewTests, self).setUp()

        self.default_view = 'partner_searches'

    def test_no_searches(self):
        url = self.get_url(company=self.company.id,
                     partner=self.partner.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        self.assertIn("Currently %s has no Saved Searches" % self.partner.name,
                      soup.get_text())

    def test_render_search_list(self):
        for _ in range(10):
            PartnerSavedSearchFactory(user=self.contact.user,
                                      provider=self.company,
                                      created_by=self.staff_user,
                                      partner=self.partner)

        # Get the page
        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        searches = soup.find(id='searches')

        self.assertEqual(len(searches('tr')), 11)


class SearchFeedTests(MyPartnersTestCase):
    """Tests relating to the search feed page, /prm/view/searches/feed"""
    def setUp(self):
        super(SearchFeedTests, self).setUp()

        self.default_view = 'partner_view_full_feed'
        self.search = PartnerSavedSearchFactory(provider=self.company,
                                                created_by=self.staff_user,
                                                user=self.contact.user,
                                                partner=self.partner)

        # Create a TestClient
        self.client = TestClient()
        self.client.login_user(self.staff_user)

    def test_details(self):
        url = self.get_url(company=self.company.id,
                           partner=self.partner.id,
                           id=self.search.id)

        response = self.client.get(url)
        soup = BeautifulSoup(response.content)

        self.assertEqual(response.status_code, 200)
        details = soup.find(id="saved-search-listing-details")

        self.assertIn('Active', details.find('h2').get_text())
        texts = ['http://www.my.jobs/jobs',
                 'Weekly on Monday',
                 'Relevance',
                 'Never',
                 'alice@example.com',
                 'All jobs from www.my.jobs']
        details = details('div', recursive=False)
        for i, text in enumerate(texts):
            self.assertIn(text, details[i].get_text())


class SearchEditTests(MyPartnersTestCase):
    """Tests relating to the edit search page /prm/view/searches/edit"""
    def setUp(self):
        super(SearchEditTests, self).setUp()

        self.default_view = 'partner_edit_search'

        self.search = PartnerSavedSearchFactory(provider=self.company,
                                                created_by=self.staff_user,
                                                user=self.contact.user,
                                                partner=self.partner)

    def test_render_new_form(self):
        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_render_existing_data(self):
        url = self.get_url(company=self.company.id,
                           partner=self.partner.id,
                           id=self.search.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        form = soup.find(id="partner-saved-search-form")

        self.assertEqual(form.find(id='id_label')['value'], "All Jobs")
        self.assertEqual(form.find(id='id_url')['value'],
                         "http://www.my.jobs/jobs")
        self.assertEqual(form.find(id='id_is_active')['checked'], 'checked')
        self.assertIn(self.contact.name, form.find(id='id_email').get_text())
        self.assertEqual(self.search.notes,
                         form.find(id='id_notes').get_text().strip())

    def test_required_fields(self):
        self.search.delete()
        url = self.get_url('partner_savedsearch_save',
                          company=self.company.id,
                          partner=self.partner.id)

        data = {'label': 'Test',
                'url': 'http://www.jobs.jobs/jobs',
                'email': self.contact.user.email,
                'frequency': 'W',
                'day_of_week': '3'}

        # Test removing a required key from day of week
        for k in data.keys():
            post = data.copy()
            del post[k]
            response = self.client.post(url, post)
            self.assertEqual(response.status_code, 200)
            errors = json.loads(response.content)
            self.assertTrue("This field is required." in errors[k],
                            msg="field %s did not have the expected error" % k)

        # Change to testing day of month
        data.update({'frequency': 'M', 'day_of_month': '3'})
        del data['day_of_week']

        for k in data.keys():
            post = data.copy()
            del post[k]
            response = self.client.post(url, post)
            self.assertEqual(response.status_code, 200)
            errors = json.loads(response.content)
            self.assertTrue("This field is required." in errors[k])

    def test_invalid_urls(self):
        self.search.delete()
        url = self.get_url('partner_savedsearch_save',
                          company=self.company.id,
                          partner=self.partner.id)

        data = {'label': 'Test',
                'url': 'http://www.google.com',
                'email': self.contact.user.email,
                'frequency': 'W',
                'day_of_week': '3'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        errors = json.loads(response.content)
        error_msg = 'That URL does not contain feed information'
        self.assertIn(error_msg, errors['url'])

    def test_create_new_saved_search(self):
        self.search.delete()
        url = self.get_url('partner_savedsearch_save',
                          company=self.company.id,
                          partner=self.partner.id)

        data = {'feed': 'http://www.jobs.jobs/jobs/rss/jobs',
                'label': 'Test',
                'url': 'http://www.jobs.jobs/jobs',
                'url_extras': '',
                'email': self.contact.user.email,
                'account_activation_message': '',
                'frequency': 'W',
                'day_of_month': '',
                'day_of_week': '3',
                'partner_message': '',
                'notes': ''}
        post = data.copy()
        post.update({'company': self.company.id,
                     'partner': self.partner.id})

        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 200)

        # Set the translated values,
        data.update({'day_of_month': None,
                    'feed': 'http://www.my.jobs/jobs/feed/rss'})
        search = PartnerSavedSearch.objects.get()
        for k, v in data.items():
            self.assertEqual(v, getattr(search, k),
                             msg="%s != %s for field %s" %
                                 (v, getattr(search, k), k))

    def test_update_existing_saved_search(self):
        url = self.get_url('partner_savedsearch_save',
                          company=self.company.id,
                          partner=self.partner.id,
                          id=self.search.id)

        data = {'feed': 'http://www.jobs.jobs/jobs/rss/jobs',
                'label': 'Test',
                'url': 'http://www.jobs.jobs/jobs',
                'url_extras': '',
                'email': self.contact.user.email,
                'account_activation_message': '',
                'frequency': 'W',
                'day_of_month': '',
                'day_of_week': '3',
                'partner_message': '',
                'notes': ''}
        post = data.copy()
        post.update({'company': self.company.id,
                     'partner': self.partner.id,
                     'id': self.search.id})

        response = self.client.post(url, post)
        self.assertEqual(response.status_code, 200)

        # Set the translated values,
        data.update({'day_of_month': None,
                    'feed': 'http://www.my.jobs/jobs/feed/rss'})
        search = PartnerSavedSearch.objects.get()
        for k, v in data.items():
            self.assertEqual(v, getattr(search, k),
                             msg="%s != %s for field %s" %
                                 (v, getattr(search, k), k))

    def test__partner_search_for_new_contact_email(self):
        """Confirms that an email is sent when a new user is created for a 
        contact because a saved search was created on that contact's behalf.
        """
        self.search.delete()
        mail.outbox = []
        new_contact = ContactFactory(partner=self.partner,
                                     email="does@not.exist")

        url = self.get_url('partner_savedsearch_save',
                           company=self.company.id,
                           partner=self.partner.id)

        data = {'feed': 'http://www.jobs.jobs/jobs/rss/jobs',
                'label': 'Test',
                'url': 'http://www.jobs.jobs/jobs',
                'url_extras': '',
                'email': new_contact.email,
                'account_activation_message': '',
                'frequency': 'W',
                'day_of_month': '',
                'day_of_week': '3',
                'partner_message': '',
                'notes': '',
                'company': self.company.id,
                'partner': self.partner.id}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 2)
        for s in [self.staff_user.get_full_name(), str(self.company),
                  'has created a job search for you']:
            self.assertIn(s, mail.outbox[1].body)

        body = re.sub(r'\s+', ' ', mail.outbox[0].body)
        for expected in ['%s created this saved search on your behalf:' % \
                             (self.staff_user.email, ),
                         'Saved Search Notification']:
            self.assertTrue(expected in body)
        self.assertFalse('delete this saved search' in body)


class EmailTests(MyPartnersTestCase):
    def setUp(self):
        # Allows for comparing datetimes
        super(EmailTests, self).setUp()
        self.data = {
            'from': self.admin.user.email,
            'subject': 'Test Email Subject',
            'text': 'Test email body',
            'key': settings.EMAIL_KEY,
        }

    def assert_contact_info_in_email(self, email):
        self.assertTrue('For additional assistance, please contact'
                        in email.body)

    def test_email_bad_contacts(self):
        start_contact_record_num = ContactRecord.objects.all().count()
        self.data['to'] = 'bademail@1.com, None, 6, bad@email.2'
        response = self.client.post(reverse('process_email'), self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactRecord.objects.all().count(),
                         start_contact_record_num)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox.pop()
        expected_str = "No contacts or contact records could be created for " \
                       "the following email addresses."
        self.assertEqual(email.from_email, settings.PRM_EMAIL)
        self.assertEqual(email.to, [self.admin.user.email])
        self.assertTrue(expected_str in email.body)
        self.assert_contact_info_in_email(email)

    def test_contact_record_and_log_creation(self):
        new_contact = ContactFactory(partner=self.partner,
                                     user=UserFactory(email="new@user.com"),
                                     email="new@user.com")
        self.data['to'] = self.contact.email
        self.data['cc'] = new_contact.email
        response = self.client.post(reverse('process_email'), self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox.pop()
        expected_str = "We have successfully created contact records for:"
        unexpected_str = "No contacts or contact records could be created " \
                         "for the following email addresses."
        self.assertEqual(email.from_email, settings.PRM_EMAIL)
        self.assertEqual(email.to, [self.admin.user.email])
        self.assertTrue(expected_str in email.body)
        self.assertFalse(unexpected_str in email.body)
        self.assert_contact_info_in_email(email)

        record = ContactRecord.objects.get(contact_email=self.contact.email)
        self.assertEqual(record.notes, self.data['text'])
        self.assertEqual(self.data['subject'], self.data['subject'])
        log_entry = ContactLogEntry.objects.get(object_id=record.pk)
        self.assertEqual(log_entry.action_flag, ADDITION)
        self.assertEqual(log_entry.user, self.admin.user)

        record = ContactRecord.objects.get(contact_email=new_contact.email)
        self.assertEqual(record.notes, self.data['text'])
        self.assertEqual(self.data['subject'], self.data['subject'])
        log_entry = ContactLogEntry.objects.get(object_id=record.pk)
        self.assertEqual(log_entry.action_flag, ADDITION)
        self.assertEqual(log_entry.user, self.admin.user)

    def test_create_new_contact(self):
        new_email = 'test@my.jobs'
        self.data['to'] = new_email
        response = self.client.post(reverse('process_email'), self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

        contact = Contact.objects.get(email=new_email, partner=self.partner)
        ContactLogEntry.objects.get(object_id=contact.pk, action_flag=ADDITION)

        email = mail.outbox.pop()
        expected_str = "Contacts have been created for the following email " \
                       "addresses:"
        self.assertEqual(email.from_email, settings.PRM_EMAIL)
        self.assertEqual(email.to, [self.admin.user.email])
        self.assertTrue(expected_str in email.body)
        self.assert_contact_info_in_email(email)

    def test_partner_email_matching(self):
        ten = PartnerFactory(owner=self.company, uri='ten.jobs', name='10',
                             pk=10)
        eleven = PartnerFactory(owner=self.company, uri='eleven.jobs',
                                name='11', pk=11)
        twelve = PartnerFactory(owner=self.company, uri='twelve.jobs',
                                name='12', pk=12)
        dup = PartnerFactory(owner=self.company, uri='my.jobs', name='dup',
                             pk=13)
        partners = [self.partner, ten, eleven, twelve, dup, ]
        emails = [
            ('match@ten.jobs', ten),
            ('match@eleven.jobs', eleven),
            ('match@twelve.jobs', twelve),
            ('twomatches@my.jobs', self.partner),
            ('nomatches@thirteen.jobs', None)
        ]

        for email in emails:
            partner = find_partner_from_email(partners, email[0])
            self.assertEqual(email[1], partner)

    def test_email_forward_parsing(self):
        self.data['text'] = '\n---------- Forwarded message ----------\n'\
                            '\n From: A third person <athird@person.test> \n'\
                            'Sent: Wednesday, February 5, 2013 1:01 AM\n'\
                            'To: A Fourth Person <afourth@person.test>\n'\
                            'Subject: Original email\n' \
                            'Original email text.' \
                            'From: A Person <thisisa@person.text>\n' \
                            'Date: Wed, Feb 5, 2014 at 9:58 AM\n' \
                            'Subject: FWD: Forward Email\n' \
                            'To: thisisnotprm@my.jobs\n'\
                            'Cc: A Cc Person <acc@person.test>,'\
                            'Another Cc Person <anothercc@person.test>\n ' \
                            'Email 1 body'

        for email in ['prm@my.jobs', 'PRM@MY.JOBS']:
            self.data['to'] = email

            self.client.post(reverse('process_email'), self.data)

            record = ContactRecord.objects.get(contact_email='thisisnotprm@my.jobs')
            expected_date_time = datetime(2014, 02, 05, 9, 58, tzinfo=utc)
            self.assertEqual(expected_date_time, record.date_time)
            self.assertEqual(self.data['text'], record.notes)
            self.assertEqual(Contact.objects.all().count(), 2)

            Contact.objects.get(email=record.contact_email).delete()
            record.delete()

    def test_double_escape_forward(self):
        self.data['to'] = 'prm@my.jobs'
        self.data['text'] = '---------- Forwarded message ----------\\r\\n'\
                            'From: A New Person <anewperson@my.jobs>\\r\\n'\
                            'Date: Wed, Mar 26, 2014 at 11:18 AM\\r\\n'\
                            'Subject: Fwd: Test number 2\\r\\n' \
                            'To: prm@my.jobs\\r\\n\\r\\n\\r'\
                            '\\n\\r\\n\\r\\n test message'

        self.client.post(reverse('process_email'), self.data)

        ContactRecord.objects.get(contact_email='anewperson@my.jobs')

    def test_timezone_awareness(self):
        self.data['to'] = self.contact.email
        dates = ['Wed, 2 Apr 2014 11:01:01 +0000',
                 'Wed, 2 Apr 2014 10:01:01 -0100',
                 'Wed, 2 Apr 2014 09:01:01 -0200',
                 'Wed, 2 Apr 2014 08:01:01 -0300',
                 'Wed, 2 Apr 2014 12:01:01 +0100', ]
        expected_dt = datetime(2014, 4, 2, 11, 1, 0, 0, tzinfo=utc)

        for date in dates:
            self.data['headers'] = "Date: %s" % date
            self.client.post(reverse('process_email'), self.data)
            # Confirm that the ContactRecord was made with the expected
            # datetime.

            record = ContactRecord.objects.all().reverse()[0]
            result_dt = record.date_time.replace(second=0, microsecond=0)
            self.assertEqual(str(result_dt), str(expected_dt))

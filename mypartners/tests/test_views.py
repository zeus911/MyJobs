# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import csv
import json
import random
from StringIO import StringIO

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core import mail
from django.http import Http404
from django.test.client import RequestFactory 
from django.utils.timezone import utc
import requests
from mymessages.models import MessageInfo

from tasks import PARTNER_LIBRARY_SOURCES

from myjobs.tests.setup import MyJobsBase
from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import UserFactory
from mydashboard.tests.factories import CompanyFactory, CompanyUserFactory
from mypartners.tests.factories import (PartnerFactory, ContactFactory,
                                        ContactLogEntryFactory, LocationFactory,
                                        ContactRecordFactory, TagFactory)
from mysearches.tests.factories import PartnerSavedSearchFactory
from datetime import datetime, date
from mypartners import views
from mypartners.models import (Contact, ContactRecord, ContactLogEntry, 
                               Partner, PartnerLibrary, ADDITION)
from mypartners.helpers import find_partner_from_email, get_library_partners
from mysearches.models import PartnerSavedSearch


class MyPartnersTestCase(MyJobsBase):
    def setUp(self):
        super(MyPartnersTestCase, self).setUp()

        # ease the creation of tests that require a request object
        self.request_factory = RequestFactory()

        # Create a user to login as
        self.staff_user = UserFactory()

        # Create a company
        self.company = CompanyFactory()
        self.company.save()
        self.admin = CompanyUserFactory(user=self.staff_user,
                                        company=self.company)
        mail.outbox = []
        self.client = TestClient()
        self.client.login_user(self.staff_user)

        # Create a partner
        self.partner = PartnerFactory(owner=self.company, pk=1)

        # Create a contact
        self.contact_user = UserFactory(email="contact@user.com")
        self.contact = ContactFactory(partner=self.partner,
                                      user=self.contact_user,
                                      email="contact@user.com")

        # Create a TestClient
        self.client = TestClient()
        self.client.login_user(self.staff_user)

    def get_url(self, view=None, **kwargs):
        if view is None:
            view = self.default_view
        args = ["%s=%s" % (k, v) for k, v in kwargs.items()]
        args = '&'.join(args)
        return reverse(view) + '?' + args


class MyPartnerViewsTests(MyPartnersTestCase):
    """Tests for the /prm/view/ page"""

    def test_prm_worthy_no_partner(self):
        """
        Confirms that the page throws a 404 rather than a 500
        when the partner id is missing.

        """
        response = self.client.post(reverse('partner_details'))
        self.assertEqual(response.status_code, 404)

    def test_prm_page_with_no_partners(self):
        """
        Tests the prm page with no partners. Also tests users that input
        /prm/view as a URL
        """
        self.partner.delete()
        response = self.client.post('/prm/view')
        soup = BeautifulSoup(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(soup.select(".prm-no-partner")), 1)

    def test_prm_page_with_a_partner(self):
        response = self.client.post('/prm/view')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertEqual(len(soup.select('.product-card')), 1)

        for _ in range(9):
            PartnerFactory(owner=self.company)

        response = self.client.post('/prm/view')
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select('.product-card')), 10)

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
        self.assertTrue(soup.select('div.card-wrapper'))

        x = 0
        while x < 9:
            ContactFactory(partner=self.partner)
            x += 1

        response = self.client.post(reverse('partner_details') +
                                    '?company=' + str(self.company.id) +
                                    '&partner=' + str(self.partner.id))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertEqual(len(soup.select('div.product-card')), 10)


class EditItemTests(MyPartnersTestCase):
    """ Test the `edit_item` view functio. 
        
        In particular, it tests that the appropriate HTTP response is reached
        depending on the URL that the user navigates to.
    """

    def setUp(self):
        super(EditItemTests, self).setUp()
        # ids start at 1 and shouldn't be an arbitrary string or unicode
        self.bad_ids = ["0", "-1", "bacon", "¥"]
        self.content_ids = dict(partner=49, contact=49)
        # requests seem to be immutable (eg., changing partner after the fact,
        # so I'm opting for lambdas here.
        self.requests = dict(
            partner=lambda **kwargs: self.request_factory.get('/prm/view/edit',
                                                              **kwargs),
            contact=lambda **kwargs: self.request_factory.get(
                '/prm/view/details/edit', dict({'partner': 1}, **kwargs)))

    def test_add_contact_with_bad_partner_id(self):
        """ Invalid partner should always result in a 404. """

        fail_msg = "The partner id %s should have raised an Http404 but didnt"

        for partner in self.bad_ids:
            request = self.requests['contact'](partner=partner, id=1)
            request.user = self.staff_user

            with self.assertRaises(Http404) as a:
                views.edit_item(request)

                if a.exception != Http404:
                    print fail_msg % partner

    def test_edit_contact_with_bad_item(self):
        """ Invalid item should result in a 404 if not 0, otherwise, should
            display the add contact form
        """

        fail_msg = ("Navigating to /prm/view/details/edit with an id of %s "
                    "should have raised an Http404 but didn't.")

        for item in self.bad_ids[1:]:
            # 
            request = self.requests['contact'](id=item)
            request.user = self.staff_user

            with self.assertRaises(Http404, msg=fail_msg % item) as cm:
                views.edit_item(request)

                if cm.exception != Http404:
                    print fail_msg % item

    def test_content_id_ignored(self):
        """ The content ID is irrelevant, and should be ignored. """

        for ct in self.content_ids.values():
            # This URL is reached when editing a contact
            contact_request = self.requests['contact'](ct=ct)
            contact_request.user = self.staff_user
            # This URL is reached when editing a partner
            partner_request = self.requests['partner'](ct=ct)
            partner_request.user = self.staff_user

            # test content id for partner
            self.assertEqual(
                views.edit_item(contact_request).status_code, 200)

            # test content id for contact
            self.assertEqual(
                views.edit_item(partner_request).status_code, 200)

    def test_add_partner_form_loaded(self):
        request = self.requests['partner']()
        request.user = self.staff_user
        response = views.edit_item(request)
        soup = BeautifulSoup(response.content)

        self.assertIn("Add Partner", soup.title.text)
        self.assertEqual("Primary Contact", soup.legend.text)

    def test_add_contact_form_loaded(self):
        # 0 is treated as an empty parameter
        for id_ in ["0", ""]:
            request = self.requests['contact'](id=id_)
            request.user = self.staff_user

            response = views.edit_item(request)
            soup = BeautifulSoup(response.content)

            self.assertIn("Add Contact", soup.title.text)

    def test_edit_contact_form_loaded(self):
        request = self.requests['contact'](id=self.contact.pk)
        request.user = self.staff_user

        response = views.edit_item(request)
        soup = BeautifulSoup(response.content)

        self.assertIn("Edit Contact", soup.title.text)
        

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

    def test_no_recent_communication_records(self):
        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)

        # Assert details about the Organization Infobox
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-communication-records')
        # Include 1 header row
        self.assertEqual(len(container('div', class_="no-highlight")), 1)
        no_records_msg = "No recent communication records."
        self.assertIn(no_records_msg,
                      container('div', class_="no-highlight")[0]
                      .get_text().strip())

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
        container = soup.find(id='recent-communication-records')
        # Include 1 header row
        self.assertEqual(len(container('div', class_="product-card")), 1)

        for row in container('div', class_="product-card"):
            title = "Test Subject  - example-contact"
            today = date.today()
            # native date time doesn't have AP format so we fake it
            month = today.strftime('%B')
            if len(month) == 3:
                month += "."
            sub_title = "%s %s, %s" % (month, today.day,
                                       today.year)
            self.assertIn(title,
                          row('div', class_="big-title")[0].get_text().strip())
            self.assertIn(sub_title,
                          row('div', class_="sub-title")[0].get_text().strip())

        # Test that only a maximum of 3 records are displayed.
        for _ in range(4):
            ContactRecordFactory(partner=self.partner)

        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-communication-records')
        self.assertEqual(len(container('div', class_="product-card")), 1)

    def test_no_recent_saved_searches(self):
        url = self.get_url(company=self.company.id,
                           partner=self.partner.id)
        response = self.client.get(url)

        # Assert details about the Organization Infobox
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-saved-searches')
        # Include 1 header row
        self.assertEqual(len(container('div', class_="no-highlight")), 1)
        no_records_msg = "No recent saved searches."
        self.assertIn(no_records_msg,
                      container('div', class_="no-highlight")[0]
                      .get_text().strip())

    def test_recent_saved_searches(self):
        user = UserFactory(email="alice@email.com")
        self.contact.user = user
        self.contact.save()

        PartnerSavedSearchFactory.create_batch(
            2, user=self.contact.user, provider=self.company,
            created_by=self.staff_user, partner=self.partner)

        url = self.get_url(company=self.company.id, partner=self.partner.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-saved-searches')

        # Include 1 header row
        self.assertEqual(len(container('div', class_="product-card")), 1)
        for row in container('div', class_="product-card"):
            title_and_status = "All Jobs Active"
            self.assertIn(title_and_status,
                          row('div', class_="big-title")[0].get_text().strip())
            self.assertIn("Sent to: alice@example.com",
                          row('div', class_="sub-title")[0].get_text().strip())

        # Test that only the first record is displayed.
        PartnerSavedSearchFactory.create_batch(
            4, user=self.contact.user, provider=self.company,
            created_by=self.staff_user, partner=self.partner)

        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        container = soup.find(id='recent-saved-searches')
        self.assertEqual(len(container('div', class_="product-card")), 1)


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
        soup = soup.find(class_='span8')
        self.assertIn('No records available.', soup.get_text().strip())

    def test_records_counts(self):
        ContactRecordFactory.create_batch(5, partner=self.partner)

        url = self.get_url(company=self.company.id, partner=self.partner.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        records = soup.find(class_='card-wrapper')
        self.assertEqual(len(records('div', class_='product-card')), 5)


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

    def test_export_dates_correct(self):
        """ Exporting contact records should honor date filters. """

        self.default_view = 'prm_export'

        ContactRecordFactory.create_batch(3, partner=self.partner)

        # this should be the only record to show up in the result
        ContactRecordFactory(partner=self.partner,
                             date_time=datetime(3025, 2, 1))

        url = self.get_url(partner=self.partner.id,
                           company=self.company.id,
                           file_format='csv',
                           date_start='2/1/3025')

        response = self.client.get(url)
        # parse the response into elements so we can count them.
        printed_records = list(csv.DictReader(StringIO(response.content)))

        self.assertEqual(len(printed_records), 1)

    def test_bleaching(self):
        """
        Makes sure html tags are correctly being stripped from the notes
        section.

        """
        notes = '<script>alert("test!");</script>'
        self.contact_record.notes = notes
        self.contact_record.save()
        url = self.get_url(partner=self.partner.id,
                           company=self.company.id)
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

        self.assertEqual(len(form(class_='profile-form-input')), 15)
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

        self.assertEqual(len(form(class_='profile-form-input')), 15)
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
        searches = soup.find(class_='span8')
        self.assertIn("No searches available.", searches.get_text().strip())

    def test_render_search_list(self):
        PartnerSavedSearchFactory.create_batch(
            10, user=self.contact.user, provider=self.company,
            created_by=self.staff_user, partner=self.partner)

        # Get the page
        url = self.get_url(company=self.company.id, partner=self.partner.id)
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        searches = soup.find(class_='span8')

        self.assertEqual(len(searches('div', class_='product-card')), 10)


class SearchFeedTests(MyPartnersTestCase):
    """Tests relating to the search feed page, /prm/view/searches/feed"""
    def setUp(self):
        super(SearchFeedTests, self).setUp()

        self.default_view = 'partner_view_full_feed'
        self.search = PartnerSavedSearchFactory(
            provider=self.company, created_by=self.staff_user,
            user=self.contact.user, partner=self.partner)
        self.search.tags.add(TagFactory())

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
        details = soup.find(class_="sidebar")
        self.assertIn('Active', details.find('h2').get_text())
        texts = ['None',
                 'Weekly on Monday',
                 'Relevance',
                 'Never',
                 'alice@example.com',
                 str(self.search.jobs_per_email),
                 self.search.tags.first().name,
                 'All jobs from www.my.jobs']
        anchor = details('a', recursive=False)
        details = details('span', recursive=False)

        self.assertEqual(anchor[0].get_text().strip(),
                         self.search.url)
        for i, text in enumerate(texts):
            self.assertIn(text, details[i].get_text().strip())


class SearchEditTests(MyPartnersTestCase):
    """Tests relating to the edit search page /prm/view/searches/edit"""
    def setUp(self):
        super(SearchEditTests, self).setUp()

        self.default_view = 'partner_edit_search'

        self.search = PartnerSavedSearchFactory(provider=self.company,
                                                created_by=self.staff_user,
                                                user=self.contact.user,
                                                partner=self.partner,)

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
                'company': self.company.id,
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
                'frequency': 'W',
                'day_of_month': '',
                'day_of_week': '3',
                'jobs_per_email': 5,
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

    def test_deactivate_partner_search(self):
        data = {'feed': 'http://www.jobs.jobs/jobs/rss/jobs',
                'label': 'Test',
                'url': 'http://www.jobs.jobs/jobs',
                'url_extras': '',
                'email': self.contact.user.email,
                'frequency': 'W',
                'day_of_month': '',
                'day_of_week': '3',
                'jobs_per_email': 5,
                'partner_message': '',
                'notes': '',
                'company': self.company.id,
                'partner': self.partner.id,
                'is_active': True}

        self.search.delete()

        # Create saved search
        url = self.get_url('partner_savedsearch_save',
                           company=self.company.id,
                           partner=self.partner.id)
        self.client.post(url, data)
        search = PartnerSavedSearch.objects.get()

        self.client.login_user(search.user)
        data['id'] = search.pk
        data['is_active'] = False
        recipient_url = self.get_url('edit_search',
                                     id=search.id,
                                     pss=True)
        mail.outbox = []
        self.assertEqual(MessageInfo.objects.count(), 0)

        # Edit saved search to toggle status of is_active
        self.client.post(recipient_url, data)
        search = PartnerSavedSearch.objects.get()

        # This should result in one email...
        email = mail.outbox[0]
        self.assertEqual(email.to[0], search.created_by.email)
        self.assertTrue('unsubscribed' in email.body)

        # ... and one My.jobs message, both to the saved search creator.
        message_info = MessageInfo.objects.get()
        self.assertEqual(message_info.user, search.created_by)
        self.assertTrue('unsubscribed' in message_info.message.body)

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
                'frequency': 'W',
                'day_of_month': '',
                'day_of_week': '3',
                'jobs_per_email': 5,
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

    def test_copy_existing_saved_search(self):
        saved_search = PartnerSavedSearch.objects.first()
        response = self.client.post('%s?company=%s&partner=%s&copies=%s' %
                                    (reverse('partner_edit_search'),
                                     self.company.id,
                                     self.partner.id, saved_search.id))

        self.assertEqual(response.status_code, 200)

        # make sure the label is a copy
        self.assertIn("Copy of %s" % saved_search.label, response.content)

    def test_partner_search_for_new_contact_email(self):
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
                'frequency': 'W',
                'day_of_month': '',
                'day_of_week': '3',
                'jobs_per_email': 10,
                'partner_message': '',
                'notes': '',
                'company': self.company.id,
                'partner': self.partner.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)


class EmailTests(MyPartnersTestCase):
    def setUp(self):
        # Allows for comparing datetimes
        super(EmailTests, self).setUp()
        self.data = {
            'from': self.staff_user.email,
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
        self.assertEqual(email.from_email, 'My.jobs Partner Relationship Manager <prm@my.jobs>')
        self.assertEqual(email.to, [self.staff_user.email])
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
        self.assertEqual(email.from_email, 'My.jobs Partner Relationship Manager <prm@my.jobs>')
        self.assertEqual(email.to, [self.staff_user.email])
        self.assertTrue(expected_str in email.body)
        self.assertFalse(unexpected_str in email.body)
        self.assert_contact_info_in_email(email)

        record = ContactRecord.objects.get(contact_email=self.contact.email)
        self.assertEqual(record.notes, self.data['text'])
        self.assertEqual(self.data['subject'], self.data['subject'])
        log_entry = ContactLogEntry.objects.get(object_id=record.pk)
        self.assertEqual(log_entry.action_flag, ADDITION)
        self.assertEqual(log_entry.user, self.staff_user)

        record = ContactRecord.objects.get(contact_email=new_contact.email)
        self.assertEqual(record.notes, self.data['text'])
        self.assertEqual(self.data['subject'], self.data['subject'])
        log_entry = ContactLogEntry.objects.get(object_id=record.pk)
        self.assertEqual(log_entry.action_flag, ADDITION)
        self.assertEqual(log_entry.user, self.staff_user)

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
        self.assertEqual(email.from_email, 'My.jobs Partner Relationship Manager <prm@my.jobs>')
        self.assertEqual(email.to, [self.staff_user.email])
        self.assertTrue(expected_str in email.body)
        self.assert_contact_info_in_email(email)

    def test_partner_email_multiple_companies(self):
        company2 = CompanyFactory(name="Company 2", pk=22222)
        CompanyUserFactory(user=self.staff_user, company=company2)

        mail.outbox = []

        new_email = 'test@my.jobs'
        self.data['to'] = new_email
        response = self.client.post(reverse('process_email'), self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Contact.objects.filter(email=new_email).count(), 0)

        email = mail.outbox.pop()
        self.assertIn('create your record manually.', email.body)

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

    def test_various_forward_header_formats(self):
        self.data['to'] = 'prm@my.jobs'
        self.data['text'] = ("Some text before the forward\n"
                            "\n"
                            "From: A New Person<anewperson@my.jobs<mailto:anewperson@my.jobs>>\n"
                            "Reply-To: A New Person<anewperson@my.jobs<mailto:anewperson@my.jobs>>\n"
                            "Date: Tuesday, July 8, 2014 2:02 PM\n"
                            "To: PRM <prm@my.jobs>\n"
                            "Subject: Test email\n"
                            "\n"
                            "Forwarded email content\n"
                            "\n")
        self.client.post(reverse('process_email'), self.data)
        ContactRecord.objects.get(contact_email='anewperson@my.jobs')
        ContactRecord.objects.all().delete()

        self.data['text'] = ("From: A New Person [mailto:anewperson@my.jobs] "
                             "On Behalf Of Someone Else\n"
                             "Sent: Wednesday, October 05, 2011 5:17 PM\n"
                             "To: prm@my.jobs\n"
                             "Subject: Stuff\n")

        self.client.post(reverse('process_email'), self.data)
        ContactRecord.objects.get(contact_email='anewperson@my.jobs')
        ContactRecord.objects.all().delete()

        self.data['text'] = ("-------- Original Message --------\n"
                             "Subject: 	Test\n"
                             "Date: 	Wed, 17 Aug 2011 11:39:46 -0400\n"
                             "From: 	A New Person <anewperson@my.jobs>\n"
                             "To: 	prm@my.jobs\n")

        self.client.post(reverse('process_email'), self.data)
        ContactRecord.objects.get(contact_email='anewperson@my.jobs')
        ContactRecord.objects.all().delete()

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

    def test_blank_to(self):
        """
        Test for PD-1150.

        Forwarded emails with blank or "bad" from/to/cc fields should not
        result in ContactRecords being created for every Contact with a blank
        email.

        Additionally, these bad emails and emails to no one except
        prm@my.jobs should generate useful error messages.

        """

        ContactFactory(partner=self.partner, email='')

        self.data['to'] = ''
        self.client.post(reverse('process_email'), self.data)

        records = ContactRecord.objects.filter(contact_email='')
        self.assertEqual(records.count(), 0)
        self.assertIn('manually create contact records for this email.',
                      mail.outbox[0].body)

        mail.outbox = []

        self.data['to'] = ''
        self.data['text'] = '---------- Forwarded message ----------\\r\\n' \
                            'From: My.jobs Partner Relationship Manager [mailto:prm@my.jobs]\\r\\n' \
                            'Date: Wed, Mar 26, 2014 at 11:18 AM\\r\\n' \
                            'Subject: Fwd: Test number 2\\r\\n' \
                            'To: AJ Selvey\\r\\n\\r\\n\\r' \
                            '\\n\\r\\n\\r\\n test message'
        self.client.post(reverse('process_email'), self.data)

        records = ContactRecord.objects.filter(contact_email='')
        self.assertEqual(records.count(), 0)
        self.assertIn('manually create contact records for this email',
                      mail.outbox[0].body)


class PartnerLibraryTestCase(MyPartnersTestCase):
    @classmethod
    def setUpClass(cls):
        url = 'mypartners/tests/data/library.html'

        super(PartnerLibraryTestCase, cls).setUpClass()
        for partner in get_library_partners(url):
            fullname = " ".join(" ".join([partner.first_name,
                                          partner.middle_name,
                                          partner.last_name]).split())

            if not PartnerLibrary.objects.filter(
                    contact_name=fullname, st=partner.st, city=partner.city):
                PartnerLibrary(
                    name=partner.organization_name, uri=partner.website,
                    region=partner.region, state=partner.state,
                    area=partner.area, contact_name=fullname,
                    phone=partner.phone, phone_ext=partner.phone_ext,
                    alt_phone=partner.alt_phone, fax=partner.fax,
                    email=partner.email_id, street1=partner.street1,
                    street2=partner.street2, city=partner.city, st=partner.st,
                    zip_code=partner.zip_code, is_minority=partner.minority,
                    is_female=partner.female, is_disabled=partner.disabled,
                    is_disabled_veteran=partner.disabled_veteran,
                    is_veteran=partner.veteran).save()
        cls.partner_library = PartnerLibrary.objects.all()


class PartnerLibraryViewTests(PartnerLibraryTestCase):

    def test_errd_reachable(self):
        # Employment Referral Resource Directory
        url, params = PARTNER_LIBRARY_SOURCES.values()[0].values()

        response = requests.post(url, params)
        self.assertEqual(response.status_code, 200)

    def test_dvcrd_reachable(self):

        # Disability and Veterans Community Resources Directory
        url, params = PARTNER_LIBRARY_SOURCES.values()[1].values()

        response = requests.post(url, params)
        self.assertEqual(response.status_code, 200)

    def test_can_create_partner_from_library(self):
        """
        Given a library id, it should be possible to create a valid partner and
        contact along with the relationships between the two.
        """
        library_id = random.randint(1, self.partner_library.count())
        request = self.request_factory.get(
            'prm/view/partner-library/add', dict(
                company=self.company.id,
                library_id=library_id))
        request.user = self.staff_user

        views.create_partner_from_library(request)

        # test that partner was in fact created
        try:
            partner = Partner.objects.get(library=library_id)
        except Partner.DoesNotExist:
            self.fail("Partner with an ID of %s not created!" % library_id)

        # ensure that the associated contact was created as well
        try:
            Contact.objects.get(library=library_id)
        except Partner.DoesNotExist:
            self.fail("Contact with an ID of %s not created!" % library_id)

        # test that appropriate tags created
        library = PartnerLibrary.objects.get(id=library_id)
        for tag in ['Veteran', 'Disabled Veteran',  
                    'Female', 'Minority']:
            if getattr(library, 'is_%s' % tag.lower().replace(' ', '_')):
                self.assertIn(tag, partner.tags.values_list('name', flat=True))

        if library.is_disabled:
            self.assertIn('Disability',
                          partner.tags.values_list('name', flat=True))


class ContactLogEntryTests(MyPartnersTestCase):
    def test_contact_record_update(self):
        record = ContactRecordFactory()

        url = self.get_url(partner=self.partner.id, company=self.company.id,
                           id=record.id, view='partner_edit_record')

        data = {
            'contact_type': 'email',
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
            'partner': self.partner.id
        }

        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, 200)
        log = ContactLogEntry.objects.get()

        delta = json.loads(log.delta)
        self.assertEqual(record.contact_email, delta['contact_email']['initial'])
        self.assertEqual(data['contact_email'], delta['contact_email']['new'])

    def test_partner_saved_search_update(self):
        search = PartnerSavedSearchFactory(created_by=self.staff_user,
                                           partner=self.partner,
                                           provider=self.company,
                                           user=self.contact_user)

        url = self.get_url('partner_savedsearch_save',
                           company=self.company.id,
                           partner=self.partner.id,
                           id=search.id)

        data = {
            'feed': 'http://www.jobs.jobs/jobs/rss/jobs',
            'label': 'Test',
            'url': 'http://www.jobs.jobs/jobs',
            'url_extras': '',
            'email': self.contact.user.email,
            'frequency': 'W',
            'day_of_month': '',
            'day_of_week': '3',
            'jobs_per_email': 5,
            'partner_message': '',
            'notes': '',
            'company': self.company.id,
            'partner': self.partner.id,
            'id': search.id
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

        log = ContactLogEntry.objects.get()

        delta = json.loads(log.delta)

        self.assertEqual(search.url, delta['url']['initial'])
        self.assertEqual(data['url'], delta['url']['new'])

    def test_partner_update(self):

        url = self.get_url(partner=self.partner.id, company=self.company.pk,
                           id=self.partner.id,
                           ct=ContentType.objects.get_for_model(Partner).pk,
                           view='save_item')

        new_contact_user = UserFactory(email="newcontact@user.com")
        new_contact = ContactFactory(partner=self.partner,
                                     user=new_contact_user,
                                     name='Fred', email=new_contact_user.email)

        data = {
            'company_id': self.company.pk,
            'name': self.partner.name,
            'primary_contact': new_contact.pk,
            'uri': 'www.google.com',
        }

        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, 200)
        log = ContactLogEntry.objects.get()

        delta = json.loads(log.delta)

        self.assertEqual(new_contact.name, delta['primary_contact']['new'])

    def test_contact_update(self):

        url = self.get_url(partner=self.partner.id, company=self.company.pk,
                           id=self.contact.id, view='save_item',
                           ct=ContentType.objects.get_for_model(Contact).pk)

        data = {
            'company_id': self.company.pk,
            'partner': self.partner.pk,
            'name': 'George',
        }

        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, 200)
        log = ContactLogEntry.objects.get()

        delta = json.loads(log.delta)

        self.assertEqual(self.contact.name, delta['name']['initial'])
        self.assertEqual(data['name'], delta['name']['new'])

    def test_location_update(self):
        location = LocationFactory()
        self.contact.locations.add(location)
        self.contact.save()

        url = self.get_url(partner=self.partner.id, company=self.company.pk,
                           id=self.contact.id, location=location.id,
                           view='edit_location')

        data = {
            'company_id': self.company.pk,
            'partner': self.partner.pk,
            'label': 'The label has changed.',
            'city': 'Fargo',
            'state': 'ND',
        }

        response = self.client.post(url, data=data, follow=True)

        self.assertEqual(response.status_code, 200)
        log = ContactLogEntry.objects.get()

        delta = json.loads(log.delta)

        self.assertEqual(location.city, delta['city']['initial'])
        self.assertEqual(data['city'], delta['city']['new'])

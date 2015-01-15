from mock import patch

from django.core import mail
from django.core.urlresolvers import reverse

from myjobs.tests.setup import MyJobsBase
from mypartners.models import Contact
from mypartners.tests.factories import ContactFactory, PartnerFactory
from mysearches.forms import SavedSearchForm, PartnerSavedSearchForm
from mysearches.tests.helpers import return_file
from mysearches.tests.factories import SavedSearchFactory
from myjobs.tests.factories import UserFactory
from registration.models import Invitation
from seo.tests import CompanyFactory


class SavedSearchFormTests(MyJobsBase):
    def setUp(self):
        super(SavedSearchFormTests, self).setUp()
        self.user = UserFactory()
        self.data = {'url': 'http://www.my.jobs/jobs',
                     'feed': 'http://www.my.jobs/jobs/feed/rss?',
                     'email': 'alice@example.com',
                     'frequency': 'D',
                     'jobs_per_email': 5,
                     'label': 'All jobs from www.my.jobs',
                     'sort_by': 'Relevance'}

        self.patcher = patch('urllib2.urlopen', return_file())
        self.patcher.start()

    def tearDown(self):
        super(SavedSearchFormTests, self).tearDown()
        self.patcher.stop()

    def test_successful_form(self):
        form = SavedSearchForm(user=self.user, data=self.data)
        self.assertTrue(form.is_valid())

    def test_invalid_url(self):
        self.data['url'] = 'http://google.com'
        form = SavedSearchForm(user=self.user, data=self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['url'][0], 'This URL is not valid.')

    def test_day_of_week(self):
        self.data['frequency'] = 'W'
        form = SavedSearchForm(user=self.user, data=self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['day_of_week'][0],
                         'This field is required.')

        self.data['day_of_week'] = '1'
        form = SavedSearchForm(user=self.user, data=self.data)
        self.assertTrue(form.is_valid())

    def test_day_of_month(self):
        self.data['frequency'] = 'M'
        form = SavedSearchForm(user=self.user, data=self.data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['day_of_month'][0],
                         'This field is required.')

        self.data['day_of_month'] = '1'
        form = SavedSearchForm(user=self.user, data=self.data)
        self.assertTrue(form.is_valid())

    def test_duplicate_url(self):
        SavedSearchFactory(user=self.user)
        form = SavedSearchForm(user=self.user, data=self.data)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['url'][0], 'URL must be unique.')


class PartnerSavedSearchFormTests(MyJobsBase):
    def setUp(self):
        super(PartnerSavedSearchFormTests, self).setUp()
        self.user = UserFactory()
        self.company = CompanyFactory()
        self.partner = PartnerFactory(owner=self.company)
        self.partner_search_data = {
            'url': 'http://www.my.jobs/jobs',
            'feed': 'http://www.my.jobs/jobs/feed/rss?',
            'frequency': 'D',
            'label': 'All jobs from www.my.jobs',
            'sort_by': 'Relevance',
            'jobs_per_email': 5,
        }

        self.patcher = patch('urllib2.urlopen', return_file())
        self.mock_urlopen = self.patcher.start()

    def tearDown(self):
        super(PartnerSavedSearchFormTests, self).tearDown()
        try:
            self.patcher.stop()
        except RuntimeError:
            # patcher was stopped in a test
            pass

    def test_partner_saved_search_form_creates_invitation(self):
        """
        Saving a partner saved search form should also create
        an invitation
        """
        contact = ContactFactory(user=None, email='new_user@example.com',
                                 partner=self.partner)
        self.partner_search_data['email'] = 'new_user@example.com'
        form = PartnerSavedSearchForm(partner=self.partner,
                                      data=self.partner_search_data)
        instance = form.instance
        instance.provider = self.company
        instance.partner = self.partner
        instance.created_by = self.user
        instance.custom_message = instance.partner_message
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(Invitation.objects.count(), 1)
        invitation = Invitation.objects.get()
        self.assertTrue(invitation.invitee.in_reserve)
        contact = Contact.objects.get(pk=contact.pk)
        self.assertEqual(invitation.invitee, contact.user)

    def test_initial_email_has_unsubscription_options(self):
        """
        The initial email received for a partner saved search should have an
        unsubscribe link included
        """

        # create and submit the form
        contact = ContactFactory(user=None, email='new_user@example.com',
                                 partner=self.partner)
        self.partner_search_data['email'] = 'new_user@example.com'
        form = PartnerSavedSearchForm(partner=self.partner,
                                      data=self.partner_search_data)
        instance = form.instance
        instance.provider = self.company
        instance.partner = self.partner
        instance.created_by = self.user
        instance.custom_message = instance.partner_message
        self.assertTrue(form.is_valid())
        form.save()

        # ensure email received with the correct content
        self.assertIn(mail.outbox[0].body, 
                      "Unsubscribe from all My.jobs emails")

from celery.exceptions import RetryTaskError
import datetime
import re

from django.conf import settings
from django.core import mail

from bs4 import BeautifulSoup
from mock import patch

from myjobs.tests.setup import MyJobsBase
from mydashboard.tests.factories import CompanyFactory
from myjobs.tests.factories import UserFactory
from mypartners.models import ContactRecord
from mypartners.tests.factories import PartnerFactory, ContactFactory
from myprofile.tests.factories import PrimaryNameFactory
from mysearches.models import SavedSearch
from mysearches.templatetags.email_tags import get_activation_link
from mysearches.tests.factories import (SavedSearchFactory,
                                        SavedSearchDigestFactory,
                                        PartnerSavedSearchFactory)
from mysearches.tests.test_helpers import return_file
from registration.models import ActivationProfile, Invitation
from tasks import send_search_digests


class SavedSearchModelsTests(MyJobsBase):
    def setUp(self):
        super(SavedSearchModelsTests, self).setUp()
        self.user = UserFactory()

        self.patcher = patch('urllib2.urlopen', return_file())
        self.mock_urlopen = self.patcher.start()

    def tearDown(self):
        super(SavedSearchModelsTests, self).tearDown()
        try:
            self.patcher.stop()
        except RuntimeError:
            # patcher was stopped in a test
            pass

    def test_send_search_email(self):
        SavedSearchDigestFactory(user=self.user,
                                 is_active=False)
        search = SavedSearchFactory(user=self.user, is_active=True,
                                    frequency='D',
                                    url='www.my.jobs/jobs?q=new+search')
        send_search_digests()
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox.pop()
        self.assertEqual(email.from_email, settings.SAVED_SEARCH_EMAIL)
        self.assertEqual(email.to, [self.user.email])
        self.assertEqual(email.subject, search.label)
        self.assertTrue("table" in email.body)
        self.assertTrue(email.to[0] in email.body)
        self.assertNotEqual(email.body.find(search.url),
                            -1,
                            "Search url was not found in email body")
        self.assertTrue("Your resume is %s%% complete" %
                        self.user.profile_completion in email.body)

    def test_send_search_digest_email(self):
        SavedSearchDigestFactory(user=self.user)
        send_search_digests()
        self.assertEqual(len(mail.outbox), 0)

        SavedSearchFactory(user=self.user)
        send_search_digests()
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox.pop()
        self.assertEqual(email.from_email, settings.SAVED_SEARCH_EMAIL)
        self.assertEqual(email.to, [self.user.email])
        self.assertEqual(email.subject, "Your Daily Saved Search Digest")
        self.assertTrue("table" in email.body)
        self.assertTrue(email.to[0] in email.body)

    def test_send_search_digest_send_if_none(self):
        SavedSearchDigestFactory(user=self.user, send_if_none=True)
        send_search_digests()
        self.assertEqual(len(mail.outbox), 0)

        SavedSearchFactory(user=self.user)
        send_search_digests()
        self.assertEqual(len(mail.outbox), 1)
    
    def test_initial_email(self):
        search = SavedSearchFactory(user=self.user, is_active=False,
                                    url='www.my.jobs/search?q=new+search')
        search.initial_email()
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox.pop()
        self.assertEqual(email.from_email, settings.SAVED_SEARCH_EMAIL)
        self.assertEqual(email.to, [self.user.email])
        self.assertEqual("My.jobs New Saved Search" in email.subject, True)
        self.assertTrue("table" in email.body)
        self.assertTrue(email.to[0] in email.body)

    def test_send_update_email(self):
        search = SavedSearchFactory(user=self.user, is_active=False,
                                    url='www.my.jobs/search?q=new+search')
        search.send_update_email('Your search is updated')
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox.pop()
        self.assertEqual(email.from_email, settings.SAVED_SEARCH_EMAIL)
        self.assertEqual(email.to, [self.user.email])
        self.assertEqual("My.jobs Saved Search Updated" in email.subject, True)
        self.assertTrue("table" in email.body)
        self.assertTrue("Your search is updated" in email.body)
        self.assertTrue(email.to[0] in email.body)

    def test_saved_search_all_jobs_link(self):
        search = SavedSearchFactory(user=self.user)
        search.send_email()

        email = mail.outbox.pop()
        # When search.url does not start with my.jobs, use it as the all jobs
        # link
        self.assertFalse(search.url.startswith('http://my.jobs'))
        self.assertNotEqual(email.body.find(search.url), -1)

        # When search.url starts with my.jobs, strip /feed/rss from search.feed
        # if it exists and use that as the all jobs link
        search.url = 'http://my.jobs/' + '1'*32
        search.save()
        search.send_email()
        email = mail.outbox.pop()
        self.assertEqual(email.body.find(search.url),
                         -1)
        self.assertNotEqual(email.body.find(search.feed.replace('/feed/rss', '')),
                            -1)

    def assert_modules_in_hrefs(self, modules):
        """
        Assert that each module in :modules: is in the set of HTML elements
        matched by li > a in an email
        """
        email = mail.outbox.pop()
        soup = BeautifulSoup(email.body)
        lis = soup.findAll('li')

        # .attrs is a dictionary, where the key is the attribute
        hrefs = [li.find('a').attrs['href'] for li in lis]

        self.assertEqual(len(hrefs), len(modules))

        # We can do self because the list of modules in settings and the list
        # of recommendations should be in the same order
        mapping = zip(modules, hrefs)
        for pair in mapping:
            # Saved search emails should have one li per required profile unit
            # that the owner does not currently have
            self.assertTrue(pair[0] in pair[1].lower())

    def test_email_profile_completion(self):

        search = SavedSearchFactory(user=self.user)
        search.send_email()
        self.assertEqual(len(settings.PROFILE_COMPLETION_MODULES), 6)
        self.assert_modules_in_hrefs(settings.PROFILE_COMPLETION_MODULES)

        PrimaryNameFactory(user=self.user)

        search.send_email()

        new_modules = [module for module in settings.PROFILE_COMPLETION_MODULES
                       if module != 'name']
        self.assertEqual(len(new_modules), 5)
        self.assert_modules_in_hrefs(new_modules)

    def test_email_contains_activate_link(self):
        search = SavedSearchFactory(user=self.user)
        self.assertTrue(self.user.is_active)
        search.send_email()
        email = mail.outbox.pop()
        self.assertFalse('activate your account' in email.body)

        self.user.is_active = False
        self.user.save()
        search.send_email()
        email = mail.outbox.pop()
        self.assertTrue('activate your account' in email.body)

    def test_fix_fixable_search(self):
        self.patcher.stop()
        SavedSearchDigestFactory(user=self.user)
        search = SavedSearchFactory(user=self.user, feed='')
        self.assertFalse(search.feed)

        # Celery raises a retry that makes the test fail. In reality
        # everything is fine, so ignore the retry-fail.
        try:
            send_search_digests()
        except RetryTaskError:
            pass
        self.assertEqual(len(mail.outbox), 0)

        search = SavedSearch.objects.get(pk=search.pk)
        self.assertTrue(search.is_active)
        self.assertTrue(search.feed)

    def test_disable_bad_search(self):
        self.patcher.stop()
        SavedSearchDigestFactory(user=self.user)
        search = SavedSearchFactory(user=self.user, feed='',
                                    url='http://example.com')
        self.assertFalse(search.feed)

        # Celery raises a retry that makes the test fail. In reality
        # everything is fine, so ignore the retry-fail.
        try:
            send_search_digests()
        except RetryTaskError:
            pass

        email = mail.outbox.pop()
        search = SavedSearch.objects.get(pk=search.pk)
        self.assertFalse(search.is_active)

        self.assertTrue('has failed URL validation' in email.body)

    def test_get_unsent_jobs(self):
        """
        When sending a saved search email, we should retrieve all new jobs since
        last send, not all new jobs based on frequency.
        """
        self.patcher.stop()
        self.patcher = patch('urllib2.urlopen',
                             return_file(time_=datetime.datetime.now() -
                                         datetime.timedelta(days=3)))
        self.mock_urlopen = self.patcher.start()
        last_sent = datetime.datetime.now() - datetime.timedelta(days=3)
        search = SavedSearchFactory(frequency='D',
                                    last_sent=last_sent,
                                    user=self.user,
                                    email=self.user.email)
        search.send_email()
        self.assertEqual(len(mail.outbox), 1)

    def test_inactive_user_receives_saved_search(self):
        self.assertEqual(len(mail.outbox), 0)
        self.user.is_active = False
        self.user.save()
        saved_search = SavedSearchFactory(user=self.user)
        saved_search.send_email()
        self.assertEqual(len(mail.outbox), 1)


class PartnerSavedSearchTests(MyJobsBase):
    def setUp(self):
        super(PartnerSavedSearchTests, self).setUp()
        self.user = UserFactory()
        self.digest = SavedSearchDigestFactory(user=self.user)
        self.company = CompanyFactory()
        self.partner = PartnerFactory(owner=self.company)
        self.contact = ContactFactory(user=self.user,
                                      partner=self.partner)
        self.partner_search = PartnerSavedSearchFactory(user=self.user,
                                                        created_by=self.user,
                                                        provider=self.company,
                                                        partner=self.partner)
        # Partner searches are normally created with a form, which creates
        # invitations as a side effect. We're not testing the form, so we
        # can fake an invitation here.
        Invitation(invitee_email=self.partner_search.email,
                   invitee=self.partner_search.user,
                   inviting_user=self.partner_search.created_by,
                   inviting_company=self.partner_search.partner.owner,
                   added_saved_search=self.partner_search).save()

        self.patcher = patch('urllib2.urlopen', return_file())
        self.mock_urlopen = self.patcher.start()
        self.num_occurrences = lambda text, search_str: [match.start()
                                                         for match
                                                         in re.finditer(
                                                             search_str, text)]
        # classes and ids may get stripped out when pynliner inlines css.
        # all jobs contain a default (blank) icon, so we can search for that if
        # we want a job count
        self.job_icon = 'http://png.nlx.org/100x50/logo.gif'

    def tearDown(self):
        super(PartnerSavedSearchTests, self).tearDown()
        try:
            self.patcher.stop()
        except RuntimeError:
            # patcher was stopped in a test
            pass

    def test_send_partner_saved_search_as_saved_search(self):
        """
        When we send saved searches, we assume they are instances of SavedSearch
        and disregard any subclasses. Ensure that partner saved searches are
        correctly recorded as sent when this happens.
        """
        search = SavedSearch.objects.get(pk=self.partner_search.pk)
        mail.outbox = []
        self.assertEqual(ContactRecord.objects.count(), 1)
        self.partner_search.send_email()
        self.assertEqual(ContactRecord.objects.count(), 2)
        partner_record = ContactRecord.objects.all()[1]
        partner_email = mail.outbox.pop()

        search.send_email()
        self.assertEqual(ContactRecord.objects.count(), 3)
        search_record = ContactRecord.objects.all()[2]
        search_email = mail.outbox.pop()

        self.assertEqual(partner_record.notes, search_record.notes)
        self.assertEqual(partner_email.body, search_email.body)
        self.assertEqual(partner_record.notes, partner_email.body)
        self.assertFalse("Your resume is %s%% complete" %
                         self.user.profile_completion in partner_email.body)

    def test_send_partner_saved_search_in_digest(self):
        """
        Saved search digests bypass the SavedSearch.send_email method. Ensure
        that partner saved searches are recorded when sent in a digest.
        """
        SavedSearchFactory(user=self.user)
        self.assertEqual(ContactRecord.objects.count(), 1)
        self.digest.send_email()
        self.assertEqual(ContactRecord.objects.count(), 2)
        email = mail.outbox[0]
        self.assertFalse("Your resume is %s%% complete" %
                         self.user.profile_completion in email.body)

    def test_send_partner_saved_search_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        mail.outbox = []
        self.partner_search.initial_email()
        email = mail.outbox.pop()
        self.assertTrue('Your account is not currently active.' in email.body)

        verify_url = get_activation_link(self.user)
        profile = ActivationProfile.objects.get(user=self.user,
                                                email=self.user.email)
        self.assertTrue(profile.activation_key in verify_url)
        self.assertTrue(self.user.user_guid in verify_url)
        self.assertTrue('https://secure.my.jobs%s' % verify_url
                        in email.body)

    def test_contact_record_created_by(self):
        ContactRecord.objects.all().delete()
        self.partner_search.initial_email()
        record = ContactRecord.objects.get()
        self.assertEqual(record.created_by, self.partner_search.created_by)

    def test_num_occurrences_instance_method(self):
        # quick sanity checks; searching for a string that doesn't exist
        # returns an empty list
        not_found = self.num_occurrences(
            'this is not the string you are looking for',
            self.job_icon)
        self.assertEqual(not_found, [])
        # searching for a string that does exist returns all starting indices
        # for the string
        found = self.num_occurrences(self.job_icon, self.job_icon)
        self.assertEqual(found, [0])

    def test_partner_saved_search_pads_results(self):
        """
        If a partner saved search results in less than the desired number of
        results, it should be padded with additional older results.

        By extension, this also tests that a normal job seeker saved search does
        not pad results.
        """

        search = SavedSearchFactory(user=self.user)
        search.send_email()
        search_email = mail.outbox.pop()
        job_count = self.num_occurrences(search_email.body, self.job_icon)
        self.assertEqual(len(job_count), 1)

        self.partner_search.send_email()
        partner_search_email = mail.outbox.pop()
        job_count = self.num_occurrences(partner_search_email.body,
                                         self.job_icon)
        self.assertEqual(len(job_count), 2)

    def test_saved_search_new_job_indicator(self):
        """
        Partner saved searches should include indicators for unseen jobs, while
        job seeker saved searches should not.
        """
        new_job_indicator = '>New! <'
        search = SavedSearchFactory(user=self.user)
        search.send_email()
        search_email = mail.outbox.pop()
        new_jobs = self.num_occurrences(search_email.body,
                                        new_job_indicator)
        self.assertEqual(len(new_jobs), 0)

        self.partner_search.send_email()
        partner_search_email = mail.outbox.pop()
        new_jobs = self.num_occurrences(partner_search_email.body,
                                        new_job_indicator)
        self.assertEqual(len(new_jobs), 1)

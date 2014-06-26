from django.conf import settings
from django.core import mail
from django.test import TestCase

from bs4 import BeautifulSoup
from mock import patch

from myjobs.tests.factories import UserFactory
from myprofile.tests.factories import PrimaryNameFactory
from mysearches.tests.factories import (SavedSearchFactory,
                                        SavedSearchDigestFactory)
from mysearches.tests.test_helpers import return_file
from registration.tests.helpers import assert_email_inlines_styles
from tasks import send_search_digests


class SavedSearchModelsTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

        self.patcher = patch('urllib2.urlopen', return_file)
        self.mock_urlopen = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

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
    
    def test_send_initial_email(self):
        search = SavedSearchFactory(user=self.user, is_active=False,
                                    url='www.my.jobs/search?q=new+search')
        search.send_initial_email()
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox.pop()
        self.assertEqual(email.from_email, settings.SAVED_SEARCH_EMAIL)
        self.assertEqual(email.to, [self.user.email])
        self.assertEqual("My.jobs New Saved Search" in email.subject, True)
        self.assertTrue("table" in email.body)
        self.assertTrue(email.to[0] in email.body)

        assert_email_inlines_styles(self, email)

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
        self.assertEqual(email.body.find(search.feed.replace('/feed/rss', '')),
                         -1)

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

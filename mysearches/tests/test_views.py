import json
import urllib2

from django.contrib.sessions.models import Session
from django.core.urlresolvers import reverse

from mock import patch

from myjobs.tests.setup import MyJobsBase
from mydashboard.tests.factories import CompanyFactory
from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import UserFactory
from mypartners.tests.factories import PartnerFactory, ContactFactory

from mysearches import forms, models
from mysearches.tests.local.fake_feed_data import jobs, no_jobs
from mysearches.tests.test_helpers import return_file
from mysearches.tests.factories import (SavedSearchDigestFactory,
                                        SavedSearchFactory,
                                        PartnerSavedSearchFactory)


class MySearchViewTests(MyJobsBase):
    def setUp(self):
        super(MySearchViewTests, self).setUp()
        self.client = TestClient()
        self.user = UserFactory()
        self.client.login_user(self.user)
        self.new_form_data = {
            'url': 'www.my.jobs/jobs',
            'feed': 'http://www.my.jobs/jobsfeed/rss?',
            'label': 'Jobs Label',
            'email': self.user.email,
            'frequency': 'D',
            'is_active': 'True',
            'jobs_per_email': 5,
            'sort_by': 'Relevance',
        }
        self.new_digest_data = {
            'is_active': 'True',
            'user': self.user,
            'email': self.user.email,
            'frequency': 'M',
            'day_of_month': 1,
        }
        self.new_form = forms.SavedSearchForm(user=self.user,
                                              data=self.new_form_data)

        self.patcher = patch('urllib2.urlopen', return_file())
        self.patcher.start()

    def tearDown(self):
        super(MySearchViewTests, self).tearDown()
        try:
            self.patcher.stop()
        except RuntimeError:
            # patcher was stopped in a test
            pass

    def test_search_main(self):
        response = self.client.get(reverse('saved_search_main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mysearches/saved_search_main.html')
        self.failUnless(isinstance(response.context['form'], forms.DigestForm))
        self.failUnless(isinstance(response.context['add_form'],
                                   forms.SavedSearchForm))

    def test_saved_search_digest_options(self):
        response = self.client.get(reverse('saved_search_main'))
        self.assertTrue('Digest Options' in response.content)
        self.assertFalse('digest-option' in response.content)

        self.assertTrue(self.new_form.is_valid())
        self.new_form.save()
        response = self.client.get(reverse('saved_search_main'))
        self.assertTrue('Digest Options' in response.content)
        self.assertTrue('digest-option' in response.content)

    def test_save_new_search_form(self):
        response = self.client.post(reverse('save_search_form'),
                                    data=self.new_form_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '')

    def test_save_new_search_invalid(self):
        del self.new_form_data['frequency']
        response = self.client.post(reverse('save_search_form'),
                                    data=self.new_form_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content).keys(),
                         ['frequency'])

    def test_get_edit_page(self):
        self.assertTrue(self.new_form.is_valid())
        self.new_form.save()
        search_id = self.new_form.instance.id
        response = self.client.get(
            reverse('edit_search')+'?id=%s' % search_id)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.new_form.instance,
                         response.context['form'].instance)
        self.assertTemplateUsed(response, 'mysearches/saved_search_edit.html')

        search_id += 1
        response = self.client.get(
            reverse('edit_search')+'id=%s' % search_id)
        self.assertEqual(response.status_code, 404)

    def test_save_edit_form(self):
        self.assertTrue(self.new_form.is_valid())
        self.new_form.save()
        search_id = self.new_form.instance.id

        self.new_form_data['frequency'] = 'W'
        self.new_form_data['day_of_week'] = 1
        self.new_form_data['url'] = 'www.my.jobs/search?'
        self.new_form_data['search_id'] = search_id

        new_form = forms.SavedSearchForm(user=self.user,
                                         data=self.new_form_data)
        response = self.client.post(reverse('save_search_form'),
                                    data=self.new_form_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '')

        del self.new_form_data['frequency']

        response = self.client.post(reverse('save_search_form'),
                                    data=self.new_form_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content).keys(), ['frequency'])

    def test_validate_url(self):
        response = self.client.post(reverse('validate_url'),
                                    data={'url': self.new_form_data['url']},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = {u'rss_url': u'http://www.my.jobs/jobs/feed/rss',
                u'feed_title': u'My.jobs - Jobs',
                u'url_status': u'valid'}

        content = json.loads(response.content)
        self.assertEqual(content['rss_url'], data['rss_url'])
        self.assertEqual(content['url_status'], data['url_status'])

        response = self.client.post(reverse('validate_url'),
                                    data={'url': 'google.com'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content),
                         {'url_status': 'not valid'})

    def test_save_digest_form(self):
        response = self.client.post(reverse('save_digest_form'),
                                    self.new_digest_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '')

        del self.new_digest_data['email']
        response = self.client.post(reverse('save_digest_form'),
                                    self.new_digest_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         '{"email": ["This field is required."]}')

    def test_unsubscribe_owned_search(self):
        """
        Unsubscribing an owned saved search should result in
        that search being deactivated
        """
        search = SavedSearchFactory(user=self.user)
        self.assertTrue(search.is_active)

        response = self.client.get(reverse('unsubscribe')+'?id=%s' % search.id)
        search = models.SavedSearch.objects.get(id=search.id)
        self.assertFalse(search.is_active)
        self.assertTemplateUsed(response,
                                'mysearches/saved_search_disable.html')

    def test_unsubscribe_unowned_search(self):
        """
        Attempting to unsubscribe using a search that isn't yours
        should result in nothing happening to the search
        """
        user = UserFactory(email='test@example.com')
        search = SavedSearchFactory(user=user)

        response = self.client.get(reverse('unsubscribe')+'?id=%s' % search.id)
        search = models.SavedSearch.objects.get(id=search.id)
        self.assertTrue(search.is_active)
        self.assertEqual(response.status_code, 404)

    def test_unsubscribe_digest(self):
        """
        Unsubscribing a saved search digest should result in all
        of the owner's saved searches being disabled
        """
        digest = SavedSearchDigestFactory(user=self.user)
        searches = []
        for url in ['www.my.jobs/search?q=python', 'jobs.jobs/search?q=django']:
            searches.append(SavedSearchFactory(url=url, user=self.user))

        for search in searches:
            self.assertTrue(search.is_active)

        response = self.client.get(reverse('unsubscribe')+'?id=digest')
        searches = list(models.SavedSearch.objects.all())
        for search in searches:
            self.assertFalse(search.is_active)
        self.assertTemplateUsed(response,
                                'mysearches/saved_search_disable.html')
        self.assertEqual(response.status_code, 200)

    def test_anonymous_unsubscribe(self):
        search = SavedSearchFactory(user=self.user)
        Session.objects.all().delete()

        # Navigating to the 'unsubscribe' page while logged out...
        response = self.client.get(
            reverse('unsubscribe')+'?id='+str(search.id))
        path = response.request.get('PATH_INFO') + "?id=" + str(search.id)
        self.assertRedirects(response, reverse('home')+'?next='+path)
        # or with the wrong email address...
        response = self.client.get(
            reverse('unsubscribe') + '?id='+str(
                search.id)+'&verify=wrong@example.com')
        # results in being redirected to the login page and the searches
        # remaining unchanged
        self.assertRedirects(response, reverse('home'))
        search = models.SavedSearch.objects.get(id=search.id)
        self.assertTrue(search.is_active)

        response = self.client.get(
            reverse('unsubscribe') + '?id=%s&verify=%s' % (
                search.id, self.user.user_guid))
        search = models.SavedSearch.objects.get(id=search.id)
        self.assertFalse(search.is_active)

    def test_delete_owned_search(self):
        search = SavedSearchFactory(user=self.user)
        self.assertEqual(models.SavedSearch.objects.count(), 1)

        response = self.client.get(
            reverse('delete_saved_search')+'?id=%s' % search.id)
        self.assertEqual(models.SavedSearch.objects.count(), 0)
        self.assertRedirects(response, reverse(
            'saved_search_main_query')+'?d='+str(urllib2.quote(
                                                 search.label)))

    def test_delete_all_searches(self):
        """
        Deleting all searches should only remove regular saved searches if the
        partner saved searches weren't created by the user trying to use it.
        """
        
        user = UserFactory(email='asdfa@example.com')
        company = CompanyFactory(id=2423, name="Bacon Factory",
                                 user_created=False)
        SavedSearchFactory(user=self.user)
        pss = PartnerSavedSearchFactory(user=self.user, created_by=user,
                                        provider=company)

        response = self.client.get(reverse('delete_saved_search') +
            '?id=ALL')
        
        self.assertEqual(response.status_code, 302)
        # partner saved search should still exist...
        self.assertTrue(models.PartnerSavedSearch.objects.filter(
            pk=pss.pk).exists())
        # ... but the regular saved search shouldn't
        self.assertFalse(models.SavedSearch.objects.filter(
            partnersavedsearch__isnull=True).exists())

    def test_delete_unowned_search(self):
        """
        Attempting to delete a search that isn't yours should
        result in nothing happening to the search
        """
        user = UserFactory(email='test@example.com')
        search = SavedSearchFactory(user=user)

        response = self.client.get(
            reverse('delete_saved_search')+'?id=%s' % search.id)
        self.assertEqual(models.SavedSearch.objects.count(), 1)
        self.assertEqual(response.status_code, 404)

    def test_delete_owned_searches_by_digest(self):
        """
        Deleting with a saved search digest should result in
        all of the user's saved searches being deleted
        """
        digest = SavedSearchDigestFactory(user=self.user)
        searches = []
        for url in ['www.my.jobs/search?q=python', 'jobs.jobs/search?q=django']:
            searches.append(SavedSearchFactory(url=url, user=self.user))

        self.assertEqual(models.SavedSearch.objects.count(), 2)

        response = self.client.get(reverse('delete_saved_search')+'?id=digest')
        self.assertEqual(models.SavedSearch.objects.count(), 0)
        self.assertRedirects(response, reverse(
            'saved_search_main_query')+'?d=all')

    def test_anonymous_delete_searches(self):
        search = SavedSearchFactory(user=self.user)
        Session.objects.all().delete()

        # Navigating to the 'delete saved search' page while logged out...
        response = self.client.get(
            reverse('delete_saved_search')+'?id='+str(search.id))
        path = response.request.get('PATH_INFO') + "?id=" + str(search.id)
        self.assertRedirects(response, reverse('home')+'?next='+path)
        self.assertEqual(models.SavedSearch.objects.count(), 1)
        # or with the wrong email address...
        response = self.client.get(
            reverse('delete_saved_search')+'?id='+str(
                search.id)+'&verify=wrong@example.com')
        # results in being redirected to the login page and no searches being
        # deleted
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(models.SavedSearch.objects.count(), 1)

        response = self.client.get(
            reverse('delete_saved_search')+'?id=%s&verify=%s' % (
                search.id, self.user.user_guid))
        self.assertEqual(models.SavedSearch.objects.count(), 0)

        # assertRedirects follows any redirect and waits for a 200 status code;
        # anonymous users will always redirect, never returning a 200.
        self.client.login_user(self.user)
        self.assertRedirects(response, reverse(
            'saved_search_main_query')+'?d='+str(urllib2.quote(
                                                 search.label)))

    def test_widget_with_saved_search(self):
        search = SavedSearchFactory(user=self.user)
        response = self.client.get(reverse('saved_search_widget') +
                                   '?url=%s&callback=callback' % (
                                       search.url, ))
        edit_url = '\\"https://secure.my.jobs%s?id=%s\\"' % (
            reverse('edit_search'), search.pk)
        self.assertTrue(edit_url in response.content)

    def test_widget_with_partner_saved_search(self):
        company = CompanyFactory()
        partner = PartnerFactory(owner=company)
        ContactFactory(user=self.user, partner=partner)
        search = PartnerSavedSearchFactory(user=self.user,
                                           created_by=self.user,
                                           provider=company,
                                           partner=partner)

        response = self.client.get(reverse('saved_search_widget') +
                                   '?url=%s&callback=callback' % (
                                       search.url, ))
        edit_url = '\\"https://secure.my.jobs%s?id=%s&pss=True\\"' % (
            reverse('edit_search'), search.pk)
        self.assertTrue(edit_url in response.content)

    def test_viewing_feed_on_bad_search(self):
        search = SavedSearchFactory(user=self.user, url='http://404.com',
                                    feed='http://404.com/feed/json')
        response = self.client.get(reverse(
            'view_full_feed') + '?id=%s' % search.id)
        self.assertIn('This site is no longer in operation.', response.content)

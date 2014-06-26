from mock import patch, Mock
from StringIO import StringIO

from django.core.urlresolvers import reverse
from django.test import TestCase

from mydashboard.tests.factories import (BusinessUnitFactory, CompanyFactory,
                                         CompanyUserFactory, SeoSiteFactory)
from myjobs.tests.factories import UserFactory
from postajob.tests.factories import JobFactory
from postajob.models import Job, SitePackage


class ViewTests(TestCase):
    def setUp(self):
        super(ViewTests, self).setUp()
        self.user = UserFactory()
        self.company = CompanyFactory()
        self.site = SeoSiteFactory()
        self.bu = BusinessUnitFactory()
        self.site.business_units.add(self.bu)
        self.site.save()
        self.company.job_source_ids.add(self.bu)
        self.company.save()
        self.company_user = CompanyUserFactory(user=self.user,
                                               company=self.company)
        self.login_user()

        self.choices_data = ('{"countries":[{"code":"USA", '
                             '"name":"United States of America"}], '
                             '"regions":[{"code":"IN", "name":"Indiana"}] }')
        self.side_effect = [self.choices_data for x in range(0, 50)]

        self.job_form_data = {
            'city': 'Indianapolis',
            'description': 'Description',
            'title': 'Job Form Data Title',
            'country': 'United States of America',
            'company': str(self.company.pk),
            'reqid': '123456',
            'apply_info': '',
            'zipcode': '46268',
            'apply_link': 'www.google.com',
            'state': 'Indiana',
            'apply_email': '',
            'apply_type': 'link',
            'post_to': 'network',
            'date_expired_1': '04',
            'date_expired_0': 'Jun',
            'date_expired_2': '2014',
        }

    def login_user(self):
        self.client.post(reverse('home'),
                         data={
                             'username': self.user.email,
                             'password': 'secret',
                             'action': 'login',
                         })

    def test_postajob_access_not_company_user(self):
        self.company_user.delete()

        response = self.client.post(reverse('jobs_overview'))
        self.assertRedirects(response, 'http://testserver/?next=/postajob/',
                             status_code=302)
        response = self.client.post(reverse('job_add'))
        self.assertRedirects(response, 'http://testserver/?next=/postajob/add',
                             status_code=302)
        response = self.client.post(reverse('job_delete', kwargs={'pk': 1}))
        expected = 'http://testserver/?next=/postajob/delete/1'
        self.assertRedirects(response, expected, status_code=302)
        response = self.client.post(reverse('job_update', kwargs={'pk': 1}))
        expected = 'http://testserver/?next=/postajob/update/1'
        self.assertRedirects(response, expected, status_code=302)

    @patch('urllib2.urlopen')
    def test_postajob_access_job_not_for_company(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        new_company = CompanyFactory(name='Another Company', pk=1000)
        job = JobFactory(company=new_company)
        kwargs = {'pk': job.pk}

        response = self.client.post(reverse('job_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('job_update', kwargs=kwargs))
        self.assertEqual(response.status_code, 404)

        # Make sure that the call to job_delete didn't delete the job
        self.assertEqual(Job.objects.all().count(), 1)

    @patch('urllib2.urlopen')
    def test_postajob_access_allowed(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        job = JobFactory(company=self.company)
        kwargs = {'pk': job.pk}

        response = self.client.post(reverse('job_update', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('job_delete', kwargs=kwargs))
        self.assertRedirects(response, 'http://testserver/postajob/',
                             status_code=302)

    @patch('urllib2.urlopen')
    def test_job_add(self, urlopen_mock):
        mock_obj = Mock()
        mock_obj.read.side_effect = self.side_effect
        urlopen_mock.return_value = mock_obj
        response = self.client.post(reverse('job_add'), data=self.job_form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.all().count(), 1)

    @patch('urllib2.urlopen')
    def test_job_update(self, urlopen_mock):
        mock_obj = Mock()
        mock_obj.read.side_effect = self.side_effect
        urlopen_mock.return_value = mock_obj
        job = JobFactory(company=self.company)
        kwargs = {'pk': job.pk}

        self.assertNotEqual(job.title, self.job_form_data['title'])
        response = self.client.post(reverse('job_update', kwargs=kwargs),
                                    data=self.job_form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.all().count(), 1)
        # Ensure we're working with the most recent copy of the job.
        job = Job.objects.get()
        self.assertEqual(job.title, self.job_form_data['title'])

    @patch('urllib2.urlopen')
    def test_job_delete(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        job = JobFactory(company=self.company)
        kwargs = {'pk': job.pk}

        response = self.client.post(reverse('job_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Job.objects.all().count(), 0)

    @patch('urllib2.urlopen')
    def test_job_add_network(self, urlopen_mock):
        mock_obj = Mock()
        mock_obj.read.side_effect = self.side_effect
        urlopen_mock.return_value = mock_obj
        response = self.client.post(reverse('job_add'), data=self.job_form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        job = Job.objects.get()
        self.assertItemsEqual(job.site_packages.all(),
                              [job.company.site_package])

    @patch('urllib2.urlopen')
    def test_job_add_site(self, urlopen_mock):
        mock_obj = Mock()
        mock_obj.read.side_effect = self.side_effect
        urlopen_mock.return_value = mock_obj
        package = SitePackage.objects.create(name='')
        package.make_unique_for_site(self.site)
        self.job_form_data['post_to'] = 'site'
        self.job_form_data['site_packages'] = self.site.pk

        response = self.client.post(reverse('job_add'), data=self.job_form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.all().count(), 1)
        job = Job.objects.get()
        # The company site_package should've never been created
        self.assertIsNone(job.company.site_package)
        # The site_package we created for the site should be
        # the package that shows up on the job.
        self.assertIn(package.pk,
                      job.site_packages.all().values_list('pk', flat=True))

    @patch('urllib2.urlopen')
    def test_job_invalid_apply(self, urlopen_mock):
        mock_obj = Mock()
        mock_obj.read.side_effect = self.side_effect
        urlopen_mock.return_value = mock_obj

        # All three
        test_data = dict(self.job_form_data)
        test_data['apply_email'] = 'email@email.email'
        test_data['apply_info'] = 'How to apply.'
        response = self.client.post(reverse('job_add'), data=test_data)
        # The lack of the redirect (302) means that the form wasn't
        # successfully submitted.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.all().count(), 0)

        # Link + Email
        test_data = dict(self.job_form_data)
        test_data['apply_email'] = 'email@email.email'
        response = self.client.post(reverse('job_add'), data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.all().count(), 0)

        # Link + Info
        test_data = dict(self.job_form_data)
        test_data['apply_info'] = 'How to apply.'
        response = self.client.post(reverse('job_add'), data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.all().count(), 0)

        # Email + Info
        test_data = dict(self.job_form_data)
        test_data['apply_link'] = ''
        test_data['apply_email'] = 'email@email.email'
        test_data['apply_info'] = 'How to apply.'
        response = self.client.post(reverse('job_add'), data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.all().count(), 0)

        #Link. Should be successful.
        test_data = dict(self.job_form_data)
        response = self.client.post(reverse('job_add'), data=test_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Job.objects.all().count(), 1)
        Job.objects.all().delete()

        # Email. Should be successful.
        test_data = dict(self.job_form_data)
        test_data['apply_link'] = ''
        test_data['apply_email'] = 'email@email.email'
        response = self.client.post(reverse('job_add'), data=test_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Job.objects.all().count(), 1)
        Job.objects.all().delete()

        # Info. Should be successful.
        test_data = dict(self.job_form_data)
        test_data['apply_link'] = ''
        test_data['apply_info'] = 'How to apply.'
        response = self.client.post(reverse('job_add'), data=test_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Job.objects.all().count(), 1)
        Job.objects.all().delete()


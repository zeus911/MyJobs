from mock import patch
from StringIO import StringIO

from django.core.urlresolvers import reverse
from django.test import TestCase

from mydashboard.tests.factories import (BusinessUnitFactory, CompanyFactory,
                                         CompanyUserFactory, SeoSiteFactory)
from myjobs.tests.factories import UserFactory
from postajob.tests.factories import JobFactory
from postajob.models import Job


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

        self.job_form_data = {
            'city': 'Indianapolis',
            'description': 'Description',
            'title': 'Job Title',
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
        self.assertEqual(response.status_code, 200)

    @patch('urllib2.urlopen')
    def test_job_add(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')

        response = self.client.post(reverse('job_add'), data=self.job_form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.all().count(), 1)

    @patch('urllib2.urlopen')
    def test_job_update(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        job = JobFactory(company=self.company)
        kwargs = {'pk': job.pk}

        response = self.client.post(reverse('job_update', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)

    @patch('urllib2.urlopen')
    def test_job_delete(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        job = JobFactory(company=self.company)
        kwargs = {'pk': job.pk}

        response = self.client.post(reverse('job_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Job.objects.all().count(), 0)
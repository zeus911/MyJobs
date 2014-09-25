# -*- coding: utf-8 -*-
import datetime

from django.conf import settings

from transform import transform_for_postajob
from seo.tests.factories import CompanyFactory
from setup import DirectSEOBase


class TransformJobs(DirectSEOBase):
    fixtures = ['import_jobs_testdata.json']

    def test_transform_for_postajob(self):
        company = CompanyFactory()

        result = {
            'city_slug': u'indianapolis',
            'full_loc_exact': 'city::Indianapolis@@state::Indiana@@location::Indianapolis, IN@@country::United States',
            'country_slab': 'usa/jobs::United States',
            'state_slab_exact': u'indiana/usa/jobs::Indiana',
            'state_short_exact': 'IN',
            'title_slab': u'job-title/jobs-in::Job Title',
            'django_ct': 'seo.joblisting',
            'guid': 0,
            'company_member': True,
            'city': 'Indianapolis',
            'country_slug': u'united-states',
            'company_ac': u'Acme Incorporated',
            'state_short': 'IN',
            'location': 'Indianapolis, IN',
            'city_ac': 'Indianapolis',
            'company_canonical_microsite': None,
            'state_ac': 'Indiana',
            'company': u'Acme Incorporated',
            'is_posted': True,
            'title_exact': 'Job Title',
            'location_exact': 'Indianapolis, IN',
            'link': 'http://my.jobs/%s',
            'company_enhanced': False,
            'state_exact': 'Indiana',
            'company_slab': u'acme-incorporated/careers::Acme Incorporated',
            'company_slab_exact': u'acme-incorporated/careers::Acme Incorporated',
            'company_exact': u'Acme Incorporated', 'country_short': 'USA',
            'job_source_name': 'Post-a-Job',
            'uid': 0,
            'reqid': 7,
            'company_digital_strategies_customer': False,
            'title_slab_exact': u'job-title/jobs-in::Job Title',
            'on_sites': ['0'],
            'id': 'postajob.job.%s',
            'django_id': 0,
            'city_slab_exact': u'indianapolis/indiana/usa/jobs::Indianapolis, IN',
            'zipcode': '46268',
            'state': 'Indiana',
            'country_ac': 'United States',
            'title_ac': 'Job Title',
            'full_loc': 'city::Indianapolis@@state::Indiana@@location::Indianapolis, IN@@country::United States',
            'country_exact': 'United States',
            'state_slab': u'indiana/usa/jobs::Indiana',
            'city_slab': u'indianapolis/indiana/usa/jobs::Indianapolis, IN',
            'state_slug': u'indiana',
            'city_exact': 'Indianapolis',
            'title_slug': u'job-title',
            'country': 'United States',
            'title': 'Job Title',
            'country_slab_exact': 'usa/jobs::United States',
            'company_canonical_microsite_exact': None,
            'apply_info': 'http://my.jobs/%s',
        }

        for i in range(0, 20):
            job = {
                'key': settings.POSTAJOB_API_KEY,
                'id': i,
                'city': 'Indianapolis',
                'company': company.id,
                'country': 'United States',
                'country_short': 'USA',
                'date_new': str(datetime.datetime.now()),
                'date_updated': str(datetime.datetime.now()),
                'description': 'This is a description of a job. It might contain 特殊字符.',
                'guid': i,
                'link': 'http://my.jobs/%s' % i,
                'apply_info': 'http://my.jobs/%s' % i,
                'on_sites': '0',
                'state': 'Indiana',
                'state_short': 'IN',
                'reqid': 7,
                'title': 'Job Title',
                'uid': i,
                'zipcode': '46268'
            }
            cleaned_job = transform_for_postajob(job)

            # These fields will never be exact, so ignore them.
            for field in ['date_updated', 'date_new', 'date_updated_exact',
                          'salted_date', 'date_new_exact', 'description',
                          'html_description', 'text']:
                del cleaned_job[field]

            # These fields are dynamically generated using id information.
            temp_result = dict(result)
            temp_result['guid'] = i
            temp_result['uid'] = i
            temp_result['link'] = result['link'] % i
            temp_result['apply_info'] = result['apply_info'] % i
            temp_result['id'] = result['id'] % i

            for key in temp_result.keys():
                self.assertEqual(cleaned_job[key], temp_result[key])
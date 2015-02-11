from datetime import datetime, timedelta
import unittest
import uuid

from bs4 import BeautifulSoup
import pysolr

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse

from seo.models import CompanyUser
from mydashboard.tests.factories import (CompanyFactory, CompanyUserFactory,
                                         SeoSiteFactory, BusinessUnitFactory)
from mydashboard.helpers import country_codes
from myjobs.tests.test_views import TestClient
from myjobs.tests.factories import UserFactory
from myprofile.tests.factories import (PrimaryNameFactory,
                                       SecondaryEmailFactory,
                                       EducationFactory, LicenseFactory,
                                       AddressFactory, TelephoneFactory,
                                       EmploymentHistoryFactory)
from mysearches.models import SavedSearch
from mysearches.tests.factories import SavedSearchFactory
from tasks import update_solr_task
from myjobs.tests.setup import MyJobsBase

SEARCH_OPTS = ['django', 'python', 'programming']


class MyDashboardViewsTests(MyJobsBase):
    def setUp(self):
        super(MyDashboardViewsTests, self).setUp()
        self.staff_user = UserFactory()
        group = Group.objects.get(name=CompanyUser.GROUP_NAME)
        self.staff_user.groups.add(group)

        self.business_unit = BusinessUnitFactory()

        self.company = CompanyFactory()
        self.company.job_source_ids.add(self.business_unit)
        self.admin = CompanyUserFactory(user=self.staff_user,
                                        company=self.company)
        self.microsite = SeoSiteFactory()
        self.microsite.business_units.add(self.business_unit)

        self.client = TestClient()
        self.client.login_user(self.staff_user)

        self.candidate_user = UserFactory(email="example@example.com")
        SavedSearchFactory(user=self.candidate_user,
                           feed='http://test.jobs/jobs/feed/rss?',
                           url='http://test.jobs/search?q=django',
                           label='test Jobs')

        for i in range(5):
            # Create 5 new users
            user = UserFactory(email='example-%s@example.com' % i)
            for search in SEARCH_OPTS:
                # Create 15 new searches and assign three per user
                SavedSearchFactory(user=user,
                                   url='http://test.jobs/search?q=%s' % search,
                                   feed='http://test.jobs/jobs/feed/rss?',
                                   label='%s Jobs' % search)
        update_solr_task(settings.TEST_SOLR_INSTANCE)

    def tearDown(self):
        super(MyDashboardViewsTests, self).tearDown()
        for location in settings.TEST_SOLR_INSTANCE.values():
            solr = pysolr.Solr(location)
            solr.delete(q='*:*')

    def add_analytics_data(self, type_, num_to_add=2):
        """
        Adds testing analytics data to Solr.

        Adds two entries per page category, one for unauthenticated and one for
        authenticated hits.
        """
        dicts = []
        base_dict = {
            'domain': self.microsite.domain,
            'view_date': datetime.now(),
            'company_id': self.company.pk,
        }
        home_dict = {
            'page_category': 'home'
        }
        view_dict = {
            'job_view_guid': '1'*32,
            'job_view_buid': self.business_unit.pk,
            'page_category': 'listing'
        }
        search_dict = {
            'page_category': 'results'
        }
        apply_dict = {
            'job_view_guid': '2'*32,
            'job_view_buid': self.business_unit.pk,
            'page_category': 'redirect'
        }

        if type_ == 'home':
            analytics_dict = home_dict
        elif type_ == 'listing':
            analytics_dict = view_dict
        elif type_ == 'results':
            analytics_dict = search_dict
        else:
            analytics_dict = apply_dict

        analytics_dict.update(base_dict)
        for _ in range(num_to_add):
            dicts.append(analytics_dict.copy())

        for analytics_dict in dicts:
            analytics_dict['aguid'] = uuid.uuid4().hex
            analytics_dict['uid'] = 'analytics##%s#%s' % (
                analytics_dict['view_date'],
                analytics_dict['aguid']
            )

        for location in settings.TEST_SOLR_INSTANCE.values():
            solr = pysolr.Solr(location)
            solr.add(dicts)

    @unittest.skip("Correct behavior undefined with respect to duplicates.")
    def test_number_of_searches_and_users_is_correct(self):
        response = self.client.post(
            reverse('dashboard')+'?company='+str(self.company.id))
        # 6 users total
        self.assertEqual(response.context['total_candidates'], 6)

        old_search = SavedSearch.objects.all()[0]
        old_search.created_on -= timedelta(days=31)
        old_search.save()

        response = self.client.post(
            reverse('dashboard')+'?company='+str(self.company.id),
            {'microsite': 'test.jobs'})

        self.assertEqual(response.context['total_candidates'], 6)

    def test_facets(self):
        education = EducationFactory(user=self.candidate_user)
        adr = AddressFactory(user=self.candidate_user)
        license = LicenseFactory(user=self.candidate_user)
        self.candidate_user.save()
        update_solr_task(settings.TEST_SOLR_INSTANCE)

        country_str = 'http://testserver/candidates/view?company=1&location={country}'
        education_str = 'http://testserver/candidates/view?company=1&education={education}'
        license_str = 'http://testserver/candidates/view?company=1&license={license_name}'

        country_str = country_str.format(country=adr.country_code)
        education_str = education_str.format(education=education.education_level_code)
        license_str = license_str.format(license_name=license.license_name)

        q = '?company={company}'
        q = q.format(company=str(self.company.id))
        response = self.client.post(reverse('dashboard')+q)
        soup = BeautifulSoup(response.content)

        types = ['Country', 'Education', 'License']
        hrefs = []
        for facet_type in types:
            container = soup.select('#%s-details-table' % facet_type)[0]
            href = container.select('a')[0].attrs['href']
            hrefs.append(href)

        self.assertIn(country_str, hrefs)
        self.assertIn(education_str, hrefs)
        self.assertIn(license_str, hrefs)

    def test_filters(self):
        adr = AddressFactory(user=self.candidate_user)
        self.candidate_user.save()
        update_solr_task(settings.TEST_SOLR_INSTANCE)

        country_str = 'http://testserver/candidates/view?company=1&amp;location={country}'
        country_filter_str = '<a class="applied-filter" href="http://testserver/candidates/view?company=1"><span>&#10006;</span> {country_long}</a><br>'
        region_str = 'http://testserver/candidates/view?company=1&amp;location={country}-{region}'
        region_filter_str = '<a class="applied-filter" href="http://testserver/candidates/view?company=1&amp;location={country}"><span>&#10006;</span> {region}, {country}</a>'
        city_str = 'http://testserver/candidates/view?company=1&amp;location={country}-{region}-{city}'
        city_filter_str = '<a class="applied-filter" href="http://testserver/candidates/view?company=1&amp;location={country}-{region}"><span>&#10006;</span> {city}, {region}, {country}</a>'

        country_str = country_str.format(country=adr.country_code)
        country_filter_str = country_filter_str.format(country=adr.country_code,
                                                       country_long=country_codes[adr.country_code])
        region_str = region_str.format(country=adr.country_code,
                                       region=adr.country_sub_division_code)
        region_filter_str = region_filter_str.format(region=adr.country_sub_division_code,
                                                     country=adr.country_code,
                                                     country_long=country_codes[adr.country_code])
        city_str = city_str.format(country=adr.country_code,
                                   region=adr.country_sub_division_code,
                                   city=adr.city_name)
        city_filter_str = city_filter_str.format(country=adr.country_code,
                                                 region=adr.country_sub_division_code,
                                                 city=adr.city_name,
                                                 country_long=country_codes[adr.country_code])

        q = '?company={company}'
        q = q.format(company=str(self.company.id))
        response = self.client.post(reverse('dashboard')+q)
        self.assertIn(country_str, response.content)

        q = '?company={company}&location={country}'
        q = q.format(company=str(self.company.id), country=adr.country_code)
        response = self.client.post(reverse('dashboard')+q)
        self.assertIn(country_filter_str, response.content)
        self.assertIn(region_str, response.content)

        q = '?company={company}&location={country}-{region}'
        q = q.format(company=str(self.company.id), country=adr.country_code,
                     region=adr.country_sub_division_code)
        response = self.client.post(reverse('dashboard')+q)
        self.assertIn(region_filter_str, response.content)
        self.assertIn(city_str, response.content)

        q = '?company={company}&location={country}-{region}-{city}'
        q = q.format(company=str(self.company.id), country=adr.country_code,
                     region=adr.country_sub_division_code,
                     city=adr.city_name)
        response = self.client.post(reverse('dashboard')+q)
        self.assertIn(city_filter_str, response.content)

    def test_search_field(self):
        # Build url
        def build_url(search):
            q = '?company={company}&search={search}'
            q = q.format(company=str(self.company.id), search=search)
            return reverse('dashboard') + q

        # assert it finds all 5 searches.
        response = self.client.post(build_url('python'))
        soup = BeautifulSoup(response.content)
        count_box = soup.select('.count-box-left')
        count = int(count_box[0].text)
        self.assertEqual(count, 5)

        # 6 users total
        response = self.client.post(build_url('example'))
        soup = BeautifulSoup(response.content)
        count_box = soup.select('.count-box-left')
        count = int(count_box[0].text)
        self.assertIn(count, [6, 7])

    def test_search_email(self):
        """We should be able to search for an exact email."""
        user = UserFactory(email="test@shouldWork.com")
        SavedSearchFactory(user=user,
                           url='http://test.jobs/search?q=python',
                           feed='http://test.jobs/jobs/feed/rss?',
                           label='Python Jobs')
        user.save()
        update_solr_task(settings.TEST_SOLR_INSTANCE)

        q = '?company={company}&search={search}'
        q = q.format(company=str(self.company.id), search='test@shouldWork.com')
        url = reverse('dashboard') + q

        response = self.client.post(url)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select('#row-link-table tr')), 1)

    def test_search_domain(self):
        """We should be able to search for domain."""
        user = UserFactory(email="test@shouldWork.com")
        SavedSearchFactory(user=user,
                           url='http://test.jobs/search?q=python',
                           feed='http://test.jobs/jobs/feed/rss?',
                           label='Python Jobs')
        user.save()
        update_solr_task(settings.TEST_SOLR_INSTANCE)

        q = '?company={company}&search={search}'
        q = q.format(company=str(self.company.id), search='shouldWork.com')
        url = reverse('dashboard') + q

        response = self.client.post(url)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select('#row-link-table tr')), 1)

    def test_search_updates_facet_counts(self):
        # Add ProfileData to the candidate_user
        EducationFactory(user=self.candidate_user)
        AddressFactory(user=self.candidate_user)
        LicenseFactory(user=self.candidate_user)
        self.candidate_user.save()

        # Create a new user with ProfileData
        user = UserFactory(email="find@testuser.com")
        SavedSearchFactory(user=user,
                           url='http://test.jobs/search?q=python',
                           feed='http://test.jobs/jobs/feed/rss?',
                           label='Python Jobs')
        EducationFactory(user=user)
        AddressFactory(user=user)
        LicenseFactory(user=user)
        user.save()

        update_solr_task(settings.TEST_SOLR_INSTANCE)

        # Assert there are two users with country codes
        country_tag = '#Country-details-table .facet-count'
        q = '?company={company}'
        q = q.format(company=str(self.company.id))
        response = self.client.post(reverse('dashboard') + q)
        soup = BeautifulSoup(response.content)
        self.assertEqual(int(soup.select(country_tag)[0].text), 2)

        # When we search, the facet count updates.
        q = '?company={company}&search={search}'
        q = q.format(company=str(self.company.id), search='find')
        response = self.client.post(reverse('dashboard') + q)
        soup = BeautifulSoup(response.content)
        self.assertEqual(int(soup.select(country_tag)[0].text), 1)

    # Tests to see if redirect from /candidates/ goes to candidates/view/
    def test_redirect_to_candidates_views_default_page(self):
        response = self.client.post('/candidates/')

        # response returns HttpResponsePermanentRedirect which returns a 301
        # status code instead of the normal 302 redirect status code
        self.assertRedirects(response, '/candidates/view/', status_code=301,
                             target_status_code=200)

        response = self.client.post(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        company_name = soup.find('h1')
        company_name = company_name.next

        self.assertEqual(company_name, self.company.name)

    # Eventually these opted-in/out will be changed to
    # track if user is part of company's activity feed
    def test_candidate_has_opted_in(self):
        response = self.client.post(
            reverse('candidate_information',
                    )+'?company='+str(self.company.id)+'&user='+str(
                        self.candidate_user.id))

        self.assertEqual(response.status_code, 200)

    def test_candidate_has_opted_out(self):
        self.candidate_user.opt_in_employers = False
        self.candidate_user.save()

        response = self.client.post(
            reverse('candidate_information',
                    )+'?company='+str(self.company.id)+'&user='+str(
                        self.candidate_user.id))
        self.assertEqual(response.status_code, 404)

    def test_candidate_page_load_with_profileunits_and_activites(self):
        # Building User with ProfileUnits
        self.name = PrimaryNameFactory(user=self.candidate_user)
        self.second_email = SecondaryEmailFactory(user=self.candidate_user)
        self.education = EducationFactory(user=self.candidate_user)
        self.address = AddressFactory(user=self.candidate_user)
        self.telephone = TelephoneFactory(user=self.candidate_user)
        self.employment = EmploymentHistoryFactory(user=self.candidate_user)
        self.candidate_user.save()
        SavedSearchFactory(user=self.candidate_user)

        response = self.client.post(
            reverse('candidate_information',
                    )+'?company='+str(self.company.id)+'&user='+str(
                        self.candidate_user.id))

        soup = BeautifulSoup(response.content)
        titles = soup.find('div', {'id': 'candidate-content'}).findAll(
            'a', {'class': 'accordion-toggle'})
        info = soup.find('div', {'id': 'candidate-content'}).findAll('li')

        self.assertEqual(len(titles), 6)
        self.assertEqual(len(info), 16)
        self.assertEqual(response.status_code, 200)

    def test_candidate_page_load_without_profileunits_with_activites(self):
        response = self.client.post(
            reverse('candidate_information',
                    )+'?company='+str(self.company.id)+'&user='+str(
                        self.candidate_user.id))

        soup = BeautifulSoup(response.content)
        titles = soup.find('div', {'id': 'candidate-content'}).findAll(
            'a', {'class': 'accordion-toggle'})
        info = soup.find('div', {'id': 'candidate-content'}).findAll('li')

        self.assertEqual(len(titles), 1)
        self.assertEqual(len(info), 3)
        self.assertEqual(response.status_code, 200)

    def test_candidate_page_load_without_profileunits_and_activites(self):
        saved_search = SavedSearch.objects.get(user=self.candidate_user)
        saved_search.delete()
        response = self.client.post(
            reverse('candidate_information',
                    )+'?company='+str(self.company.id)+'&user='+str(
                        self.candidate_user.id))

        soup = BeautifulSoup(response.content)
        info = soup.find('div', {'id': 'candidate-content'})

        self.assertFalse(info)
        self.assertEqual(response.status_code, 404)

    def test_export_csv(self):
        response = self.client.post(
            reverse('export_candidates')+'?company=' +
            str(self.company.id)+'&ex-t=csv')
        self.assertTrue(response.content)
        self.assertEqual(response.status_code, 200)

    def test_export_xml(self):
        response = self.client.post(
            reverse('export_candidates')+'?company=' +
            str(self.company.id)+'&ex-t=xml')
        self.assertTrue(response.content.index('candidates'))
        self.assertEqual(response.status_code, 200)

    def test_export_json(self):
        response = self.client.post(
            reverse('export_candidates')+'?company=' +
            str(self.company.id)+'&ex-t=json')
        self.assertTrue(response.content.index('candidates'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_analytics_no_data(self):
        response = self.client.post(
            reverse('dashboard')+'?company='+str(self.company.id),
            {'microsite': 'test.jobs'})

        soup = BeautifulSoup(response.content)

        for selector in ['#total-clicks',
                         '#total-home',
                         '#total-job-views',
                         '#total-search']:

            container = soup.select(selector)
            # Empty list means no elements were found.
            self.assertEqual(container, [])

    def test_dashboard_analytics_with_data(self):
        for type_ in ['home', 'listing', 'results']:
            self.add_analytics_data(type_)
        num_clicks = 1234
        self.add_analytics_data('redirect', num_to_add=num_clicks)

        response = self.client.post(
            reverse('dashboard')+'?company='+str(self.company.id))

        soup = BeautifulSoup(response.content)

        for selector in ['#total-clicks',
                         '#total-home',
                         '#total-job-views',
                         '#total-search']:

            # This should be the parent container for all analytics data
            # of this type
            container = soup.select(selector)[0]

            # All hits, humanized
            all_hits = container.select('span')[0]
            if selector == '#total-clicks':
                expected = '1.2k'
            else:
                expected = '2'
            self.assertEqual(all_hits.text.strip(), expected)

            # All hits, raw number
            if selector == '#total-clicks':
                full = container.attrs['data-original-title']
                self.assertEqual(full.strip(),
                                 '1,234')
            else:
                with self.assertRaises(KeyError):
                    # This is marked as having no effect, which is intended
                    container.attrs['data-original-title']

    def test_dashboard_with_no_microsites(self):
        """
        Trying to access the dashboard of a company that has no microsites
        associated with it should not create malformed solr queries.
        """
        self.microsite.delete()
        response = self.client.post(
            reverse('dashboard')+'?company='+str(self.company.id))
        self.assertEqual(response.status_code, 200)

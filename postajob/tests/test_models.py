import datetime
from mock import patch
from StringIO import StringIO
from urlparse import parse_qs

from django.conf import settings
from django.test import TestCase

from mydashboard.tests.factories import (BusinessUnitFactory, CompanyFactory,
                                         SeoSiteFactory)
from postajob.models import (Job, Product, PurchasedJob, PurchasedProduct,
                             SitePackage)


class ModelTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.site = SeoSiteFactory()
        self.bu = BusinessUnitFactory()
        self.site.business_units.add(self.bu)
        self.site.save()
        self.company.job_source_ids.add(self.bu)
        self.company.save()

        self.job_data = {
            'title': 'title',
            'company': self.company,
            'reqid': '1',
            'description': 'sadfljasdfljasdflasdfj',
            'apply_link': 'www.google.com',
            'city': 'Indianapolis',
            'state': 'Indiana',
            'state_short': 'IN',
            'country': 'United States of America',
            'country_short': 'USA',
            'zipcode': '46268',
            'date_new': datetime.datetime.now(),
            'date_updated': datetime.datetime.now(),
            'date_expired': datetime.date.today(),
            'guid': 'abcdef123456',
        }
        self.request_data = {
            'title': 'title',
            'company': self.company.id,
            'reqid': '1',
            'description': 'sadfljasdfljasdflasdfj',
            'link': 'www.google.com',
            'city': 'Indianapolis',
            'state': 'Indiana',
            'state_short': 'IN',
            'country': 'United States of America',
            'country_short': 'USA',
            'zipcode': '46268',
            'guid': 'abcdef123456',
            'on_sites': '0',
            'apply_info': '',
        }
        self.site_package_data = {
            'name': 'Test Site Package',
        }

    @patch('urllib2.urlopen')
    def test_job_creation(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('{"jobs_added": 1}')
        Job.objects.create(**self.job_data)
        self.assertEqual(Job.objects.all().count(), 1)

    @patch('urllib2.urlopen')
    def test_job_deletion(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('{"jobs_deleted": 1}')
        job = Job.objects.create(**self.job_data)
        self.assertEqual(Job.objects.all().count(), 1)
        job.delete()
        self.assertEqual(Job.objects.all().count(), 0)

    @patch('urllib2.urlopen')
    def test_job_add_to_solr(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('{"jobs_added": 1}')
        Job.objects.create(**self.job_data)
        # add_to_solr() is called in save(), so urlopen should've been
        # called once at this point.
        self.assertEqual(urlopen_mock.call_count, 1)

        # Determine what is being sent to microsites by parsing the
        # Request object passed to urlopen().
        args, _ = urlopen_mock.call_args
        data = parse_qs(args[0].data)
        data['jobs'] = eval(data['jobs'][0])
        self.assertEqual(data['key'][0], settings.POSTAJOB_API_KEY)
        for field in self.request_data.keys():
            self.assertEqual(data['jobs'][0][field], self.request_data[field])

    @patch('urllib2.urlopen')
    def test_job_remove_from_solr(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('{"jobs_deleted": 1}')
        job = Job.objects.create(**self.job_data)
        job.remove_from_solr()

        # add_to_solr() is called in save(), which is combined with the
        # call to remove_from_solr().
        self.assertEqual(urlopen_mock.call_count, 2)

        # Determine what is being sent to microsites by parsing the
        # Request object passed to urlopen().
        args, _ = urlopen_mock.call_args
        data = parse_qs(args[0].data)
        self.assertEqual(data['key'][0], settings.POSTAJOB_API_KEY)
        self.assertEqual(data['guids'][0], self.request_data['guid'])

    @patch('urllib2.urlopen')
    def test_job_generate_guid(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')

        # Confirm that pre-assigned guids are not being overwritten.
        job = Job.objects.create(**self.job_data)
        self.assertEqual(self.job_data['guid'], job.guid)
        job.delete()

        # Confirm that if a guid isn't assigned one is getting assigned
        # to it properly.
        guid = self.job_data['guid']
        del self.job_data['guid']
        job = Job.objects.create(**self.job_data)
        self.assertIsNotNone(job.guid)
        self.assertNotEqual(job.guid, guid)

    def test_site_package_make_unique_for_site(self):
        package = SitePackage.objects.create(**self.site_package_data)
        package.make_unique_for_site(self.site)
        self.assertEqual(self.site.site_package, package)
        package.delete()

        package = SitePackage.objects.create(**self.site_package_data)
        for x in range(100, 110):
            site = SeoSiteFactory(id=x, domain="%s.jobs" % x)
            package.sites.add(site)

        # Site packages with existing sites associated with it should still
        # only end up with one associated site.
        site = SeoSiteFactory(id=4000, domain="4000.jobs")
        package.make_unique_for_site(site)
        self.assertEqual(site.site_package, package)

    def test_site_package_make_unique_for_company(self):
        package = SitePackage.objects.create(**self.site_package_data)
        package.make_unique_for_company(self.company)
        self.assertEqual(self.company.site_package, package)
        package.delete()

        package = SitePackage.objects.create(**self.site_package_data)
        for x in range(1000, 1003):
            site = SeoSiteFactory(id=x, domain="%s.jobs" % x)
            package.sites.add(site)
        self.assertItemsEqual(package.sites.all().values_list('id', flat=True),
                              [1000, 1001, 1002])
        for x in range(100, 103):
            site = SeoSiteFactory(id=x, domain="%s.jobs" % x)
            site.business_units.add(self.bu)
            site.save()
        # Site packages with existing sites associated with it should
        # only end up with the sites for a company.
        package.make_unique_for_company(self.company)
        self.assertEqual(self.company.site_package, package)
        self.assertItemsEqual(package.sites.all().values_list('id', flat=True),
                              [100, 101, 102, 2])

    def create_purchased_job(self, pk=None):
        if not hasattr(self, 'package'):
            self.package = SitePackage.objects.create(**self.site_package_data)
        if not hasattr(self, 'product'):
            self.product = Product.objects.create(site_package=self.package,
                                                  cost='100.00',
                                                  owner=self.company)
        if not hasattr(self, 'purchased_product'):
            self.purchased_product = PurchasedProduct.objects.create(
                product=self.product, owner=self.company)
        self.job_data['max_expired_date'] = datetime.date.today() + datetime.timedelta(days=1)
        self.job_data['purchased_product'] = self.purchased_product
        self.job_data['pk'] = pk
        return PurchasedJob.objects.create(**self.job_data)

    @patch('urllib2.urlopen')
    def test_purchased_job_add(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        self.create_purchased_job()
        self.assertEqual(PurchasedJob.objects.all().count(), 1)
        self.assertEqual(SitePackage.objects.all().count(), 1)
        package = SitePackage.objects.get()
        job = PurchasedJob.objects.get()
        self.assertItemsEqual(job.site_packages.all(), [package])

    @patch('urllib2.urlopen')
    def test_purchased_job_add_to_solr(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        job = self.create_purchased_job()
        # Add to solr and delete from solr shouldn't be called until
        # the job is approved.
        self.assertEqual(urlopen_mock.call_count, 0)
        job.is_approved = True
        job.save()
        # Now that the job is approved, it should've been sent to solr.
        self.assertEqual(urlopen_mock.call_count, 1)

    def test_purchased_product_jobs_remaining(self):
        del self.job_data['guid']
        field = Product._meta.get_field_by_name('num_jobs_allowed')
        expected_num_jobs = field[0].default
        for x in range(50, 55):
            self.create_purchased_job()
            expected_num_jobs -= 1
            self.assertEqual(self.purchased_product.jobs_remaining(),
                             expected_num_jobs)

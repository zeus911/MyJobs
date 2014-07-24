from datetime import date, timedelta
from mock import patch, Mock
from StringIO import StringIO
from urlparse import parse_qs

from django.conf import settings
from django.contrib.auth.models import Group
from django.core import mail

from mydashboard.tests.factories import (BusinessUnitFactory, CompanyFactory,
                                         SeoSiteFactory)
from seo.models import CompanyUser
from myjobs.models import User
from postajob.models import (CompanyProfile, Job, JobLocation, OfflineProduct,
                             Product, ProductGrouping, ProductOrder,
                             PurchasedJob, PurchasedProduct, Request,
                             SitePackage)
from postajob.tests.factories import (job_factory, joblocation_factory,
                                      product_factory, offlineproduct_factory,
                                      offlinepurchase_factory,
                                      purchasedjob_factory,
                                      purchasedproduct_factory,
                                      sitepackage_factory)
from myjobs.tests.setup import MyJobsBase


class ModelTests(MyJobsBase):
    def setUp(self):
        super(ModelTests, self).setUp()
        self.user = User.objects.create(email='user@test.email')
        self.company = CompanyFactory()
        CompanyProfile.objects.create(company=self.company)
        self.site = SeoSiteFactory()
        self.bu = BusinessUnitFactory()
        self.site.business_units.add(self.bu)
        self.site.save()
        self.company.job_source_ids.add(self.bu)
        self.company.save()

        self.request_data = {
            'title': 'title',
            'company': self.company.id,
            'reqid': '1',
            'description': 'sadfljasdfljasdflasdfj',
            'link': 'www.google.com',
            'on_sites': '0',
            'apply_info': '',
        }

        self.request_location = {
            'city': 'Indianapolis',
            'state': 'Indiana',
            'state_short': 'IN',
            'country': 'United States of America',
            'country_short': 'USA',
            'zipcode': '46268',
        }

        self.site_package_data = {
            'name': 'Test Site Package',
        }

        self.choices_data = ('{"countries":[{"code":"USA", '
                             '"name":"United States of America"}], '
                             '"regions":[{"code":"IN", "name":"Indiana"}] }')
        self.side_effect = [self.choices_data for x in range(0, 50)]

    @patch('urllib2.urlopen')
    def test_job_creation_and_deletion(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('{"jobs_deleted": 1}')
        locations = [joblocation_factory() for x in range(0, 5)]
        job = job_factory(self.company, self.user)
        job.locations = locations
        job.save()
        self.assertEqual(Job.objects.all().count(), 1)
        self.assertEqual(JobLocation.objects.all().count(), 5)
        job.delete()
        self.assertEqual(Job.objects.all().count(), 0)
        self.assertEqual(JobLocation.objects.all().count(), 0)

    @patch('urllib2.urlopen')
    def test_job_add_to_solr(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('{"jobs_added": 1}')
        job = job_factory(self.company, self.user)
        job.locations.add(joblocation_factory())
        job.add_to_solr()
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
        for field in self.request_location.keys():
            self.assertEqual(data['jobs'][0][field], self.request_location[field])


    @patch('urllib2.urlopen')
    def test_job_remove_from_solr(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('{"jobs_deleted": 1}')
        job = job_factory(self.company, self.user)
        locations = [joblocation_factory() for x in range(0, 2)]
        job.locations = locations
        job.save()
        job.remove_from_solr()

        guids = [unicode(location.guid) for location in locations]

        # add_to_solr() is called in save(), which is combined with the
        # call to remove_from_solr().
        self.assertEqual(urlopen_mock.call_count, 2)

        # Determine what is being sent to microsites by parsing the
        # Request object passed to urlopen().
        args, _ = urlopen_mock.call_args
        data = parse_qs(args[0].data)
        self.assertEqual(data['key'][0], settings.POSTAJOB_API_KEY)
        self.assertItemsEqual(eval(data['guids'][0]), guids)

    @patch('urllib2.urlopen')
    def test_job_generate_guid(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        guid = '1'*32

        # Confirm that pre-assigned guids are not being overwritten.
        location = joblocation_factory(guid=guid)
        self.assertEqual(guid, location.guid)
        location.delete()

        # Confirm that if a guid isn't assigned one is getting assigned
        # to it properly.
        location = joblocation_factory()
        self.assertIsNotNone(location.guid)
        self.assertNotEqual(location.guid, guid)

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
            self.package = sitepackage_factory(self.company)
        if not hasattr(self, 'product'):
            self.product = product_factory(self.package, self.company)
        if not hasattr(self, 'purchased_product'):
            self.purchased_product = purchasedproduct_factory(self.product,
                                                              self.company)
        exp_date = date.today() + timedelta(self.product.posting_window_length)
        self.assertEqual(self.purchased_product.expiration_date, exp_date)
        return purchasedjob_factory(self.company, self.user,
                                    self.purchased_product, pk=pk)

    @patch('urllib2.urlopen')
    def test_purchased_job_add(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        self.create_purchased_job()
        self.assertEqual(PurchasedJob.objects.all().count(), 1)
        self.assertEqual(SitePackage.objects.all().count(), 1)
        self.assertEqual(Request.objects.all().count(), 1)
        package = SitePackage.objects.get()
        job = PurchasedJob.objects.get()
        self.assertItemsEqual(job.site_packages.all(), [package])

    @patch('urllib2.urlopen')
    def test_purchased_job_add_to_solr(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        job = self.create_purchased_job()
        job.locations.add(joblocation_factory())
        job.save()
        # Add to solr and delete from solr shouldn't be called until
        # the job is approved.
        self.assertEqual(urlopen_mock.call_count, 0)
        job.is_approved = True
        # Jobs won't be added/deleted until it's confirmed that the
        # purchased product is paid for as well.
        job.purchased_product.paid = True
        job.purchased_product.save()
        job.save()
        # Now that the job is approved, it should've been sent to solr.
        self.assertEqual(urlopen_mock.call_count, 1)

    def test_purchased_product_jobs_remaining(self):
        num_jobs_allowed = Product._meta.get_field_by_name('num_jobs_allowed')
        expected_num_jobs = num_jobs_allowed[0].default
        for x in range(50, 50 + expected_num_jobs):
            if hasattr(self, 'purchased_product'):
                self.assertTrue(self.purchased_product.can_post_more())
            self.create_purchased_job()
            expected_num_jobs -= 1
            self.assertEqual(self.purchased_product.jobs_remaining,
                             expected_num_jobs)
        self.assertFalse(self.purchased_product.can_post_more())

    def test_invoice_send_invoice_email(self):
        self.create_purchased_job()
        group, _ = Group.objects.get_or_create(name=Product.ADMIN_GROUP_NAME)

        # No one to recieve the email.
        self.purchased_product.invoice.send_invoice_email()
        self.assertEqual(len(mail.outbox), 0)

        # Only recipient is specified recipient.
        self.purchased_product.invoice.send_invoice_email(['this@isa.test'])
        self.assertItemsEqual(mail.outbox[0].to,
                              ['this@isa.test'])

        mail.outbox = []

        # Only recipients are admins.
        user = CompanyUser.objects.create(user=self.user, company=self.company)
        user.group.add(group)
        user.save()
        self.purchased_product.invoice.send_invoice_email()
        self.assertItemsEqual(mail.outbox[0].to,
                              [u'user@test.email'])
        self.assertItemsEqual(mail.outbox[0].from_email,
                              'invoice@my.jobs')

        mail.outbox = []

        self.company.companyprofile.outgoing_email_domain = 'test.domain'
        self.company.companyprofile.save()

        # Recipients are admins + specified recipients.
        self.purchased_product.invoice.send_invoice_email(['this@isa.test'])
        self.assertItemsEqual(mail.outbox[0].to,
                              ['this@isa.test', u'user@test.email'])
        self.assertItemsEqual(mail.outbox[0].from_email,
                              'invoice@test.domain')

    def test_productgrouping_add_delete(self):
        self.create_purchased_job()
        ProductGrouping.objects.create(display_title='Test Grouping',
                                       explanation='Test Grouping',
                                       name='Test Grouping',
                                       owner=self.company)
        self.assertEqual(ProductGrouping.objects.all().count(), 1)
        grouping = ProductGrouping.objects.get()

        order = ProductOrder.objects.create(product=self.product,
                                            group=grouping)
        grouping_products = grouping.products.all().values_list('pk', flat=True)
        self.assertItemsEqual(grouping_products, [order.pk])

        grouping.delete()
        self.assertEqual(ProductGrouping.objects.all().count(), 0)
        self.assertEqual(ProductOrder.objects.all().count(), 0)

    @patch('urllib2.urlopen')
    def test_request_generation(self, urlopen_mock):
        mock_obj = Mock()
        mock_obj.read.side_effect = self.side_effect
        urlopen_mock.return_value = mock_obj

        cu = CompanyUser.objects.create(user=self.user,
                                        company=self.company)
        cu.make_purchased_microsite_admin()

        self.create_purchased_job()
        self.assertEqual(PurchasedJob.objects.all().count(), 1)
        self.assertEqual(Request.objects.all().count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertItemsEqual(mail.outbox[0].from_email,
                              'request@my.jobs')
        mail.outbox = []

        # Already approved jobs should not generate an additional request.
        purchasedjob_factory(self.company, self.user, self.purchased_product,
                             is_approved=True)
        self.assertEqual(PurchasedJob.objects.all().count(), 2)
        self.assertEqual(Request.objects.all().count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_offlinepurchase_create_purchased_products(self):
        user = CompanyUser.objects.create(user=self.user, company=self.company)
        offline_purchase = offlinepurchase_factory(self.company, user)
        package = sitepackage_factory(self.company)
        product = product_factory(package, self.company)

        for x in range(1, 15):
            PurchasedProduct.objects.all().delete()
            OfflineProduct.objects.all().delete()
            offlineproduct_factory(product, offline_purchase,
                                   product_quantity=x)
            offline_purchase.create_purchased_products(self.company)
            self.assertEqual(PurchasedProduct.objects.all().count(), x)

        product_two = product_factory(package, self.company)
        for x in range(1, 15):
            PurchasedProduct.objects.all().delete()
            OfflineProduct.objects.all().delete()
            offlineproduct_factory(product, offline_purchase,
                                   product_quantity=x)
            offlineproduct_factory(product_two, offline_purchase,
                                   product_quantity=x)
            offline_purchase.create_purchased_products(self.company)
            self.assertEqual(PurchasedProduct.objects.all().count(), x*2)


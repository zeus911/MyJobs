from datetime import date, timedelta
from mock import patch, Mock
from StringIO import StringIO

from django.core.urlresolvers import reverse
from django.test import TestCase

from mydashboard.tests.factories import (BusinessUnitFactory, CompanyFactory,
                                         CompanyUserFactory, SeoSiteFactory)
from myjobs.tests.factories import UserFactory
from postajob.tests.factories import (product_factory, job_factory,
                                      productgrouping_factory,
                                      purchasedproduct_factory,
                                      sitepackage_factory)
from postajob.models import (Job, Package, Product, ProductGrouping,
                             PurchasedProduct, SitePackage)


class ViewTests(TestCase):
    def setUp(self):
        super(ViewTests, self).setUp()
        self.user = UserFactory()
        self.company = CompanyFactory(product_access=True)
        self.site = SeoSiteFactory()
        self.bu = BusinessUnitFactory()
        self.site.business_units.add(self.bu)
        self.site.save()
        self.company.job_source_ids.add(self.bu)
        self.company.save()
        self.company_user = CompanyUserFactory(user=self.user,
                                               company=self.company)
        sitepackage_factory(self.company)
        self.package = Package.objects.get()
        self.product = product_factory(self.package, self.company)

        self.login_user()

        self.choices_data = ('{"countries":[{"code":"USA", '
                             '"name":"United States of America"}], '
                             '"regions":[{"code":"IN", "name":"Indiana"}] }')
        self.side_effect = [self.choices_data for x in range(0, 50)]

        # Form data
        self.product_form_data = {
            'package': str(self.package.pk),
            'owner': str(self.company.pk),
            'name': 'Test Product',
            'cost': '5',
            'posting_window_length': 30,
            'max_job_length': 30,
            'num_jobs_allowed': '5',
            'description': 'Test product description.'
        }

        self.productgrouping_form_data = {
            'products': str(self.product.pk),
            'display_order': 10,
            'display_title': 'Test Grouping',
            'explanation': 'Test grouping explanation.',
            'name': 'Test Gruping',
            'owner': str(self.company.pk)
        }

        self.job_form_data = {
            'city': 'Indianapolis',
            'description': 'Description',
            'title': 'Job Form Data Title',
            'country': 'United States of America',
            'owner': str(self.company.pk),
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

        self.purchasedproduct_form_data = {
            'address_line_one': '123 Street Rd.',
            'card_number': '4007000000027',
            'city': 'Indianapolis',
            'country': 'USA',
            'cvv': '123',
            'exp_date_0': date.today().month + 1,
            'exp_date_1': date.today().year + 5,
            'first_name': 'John',
            'last_name': 'Smith',
            'state': 'Indiana',
            'zipcode': '46268',
        }

    def login_user(self):
        self.client.post(reverse('home'),
                         data={
                             'username': self.user.email,
                             'password': 'secret',
                             'action': 'login',
                         })

    def test_job_access_not_company_user(self):
        self.company_user.delete()

        response = self.client.post(reverse('jobs_overview'))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('job_add'))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('job_delete', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('job_update', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 404)

    @patch('urllib2.urlopen')
    def test_job_access_not_for_company(self, urlopen_mock):
        urlopen_mock.return_value = StringIO('')
        new_company = CompanyFactory(name='Another Company', pk=1000)
        job = job_factory(new_company, self.user)
        kwargs = {'pk': job.pk}

        response = self.client.post(reverse('job_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('job_update', kwargs=kwargs))
        self.assertEqual(response.status_code, 404)

        # Make sure that the call to job_delete didn't delete the job
        self.assertEqual(Job.objects.all().count(), 1)

    @patch('urllib2.urlopen')
    def test_job_access_allowed(self, urlopen_mock):
        mock_obj = Mock()
        mock_obj.read.side_effect = self.side_effect
        urlopen_mock.return_value = mock_obj
        job = job_factory(self.company, self.user)
        kwargs = {'pk': job.pk}

        response = self.client.post(reverse('job_update', kwargs=kwargs),
                                    data=self.job_form_data)
        self.assertRedirects(response, 'http://testserver/postajob/jobs/',
                             status_code=302)
        response = self.client.post(reverse('job_delete', kwargs=kwargs))
        self.assertRedirects(response, 'http://testserver/postajob/jobs/',
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
        job = job_factory(self.company, self.user)
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
        job = job_factory(self.company, self.user)
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
                              [job.owner.site_package])

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
        self.assertIsNone(job.owner.site_package)
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

    def test_product_add(self):
        response = self.client.post(reverse('product_add'),
                                    data=self.product_form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        # Should get the product just added + self.product
        self.assertEqual(Product.objects.all().count(), 2)

    def test_product_update(self):
        self.product_form_data['name'] = 'New Title'
        kwargs = {'pk': self.product.pk}

        self.assertNotEqual(self.product.name, self.product_form_data['name'])
        response = self.client.post(reverse('product_update', kwargs=kwargs),
                                    data=self.product_form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Product.objects.all().count(), 1)

        product = Product.objects.get()
        self.assertEqual(product.name, self.product_form_data['name'])

    def test_product_delete(self):
        self.product_form_data['name'] = 'New Title'
        kwargs = {'pk': self.product.pk}

        response = self.client.post(reverse('product_delete', kwargs=kwargs))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Job.objects.all().count(), 0)

    def test_productgrouping_add(self):
        response = self.client.post(reverse('productgrouping_add'),
                                    data=self.productgrouping_form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductGrouping.objects.all().count(), 1)

    def test_productgrouping_update(self):
        group = productgrouping_factory(self.company)
        self.productgrouping_form_data['name'] = 'New Title'
        kwargs = {'pk': group.pk}

        self.assertNotEqual(group.name, self.productgrouping_form_data['name'])
        response = self.client.post(reverse('productgrouping_update',
                                            kwargs=kwargs),
                                    data=self.productgrouping_form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ProductGrouping.objects.all().count(), 1)

        group = ProductGrouping.objects.get()
        self.assertEqual(group.name, self.productgrouping_form_data['name'])

    def test_productgrouping_delete(self):
        group = productgrouping_factory(self.company)
        self.product_form_data['name'] = 'New Title'
        kwargs = {'pk': group.pk}

        response = self.client.post(reverse('productgrouping_delete',
                                            kwargs=kwargs))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProductGrouping.objects.all().count(), 0)

    def test_purchasedproduct_add(self):
        product = {'product': self.product.pk}
        response = self.client.post(reverse('purchasedproduct_add',
                                            kwargs=product),
                                    data=self.purchasedproduct_form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PurchasedProduct.objects.all().count(), 1)

    def test_purchasedproduct_add_card_declined(self):
        # Change the card number so it doesn't artificially get declined
        # due to duplicate transactions.
        self.purchasedproduct_form_data['card_number'] = 4012888818888
        # 70.02 should always result in a decline for test cards.
        self.product.cost = 70.02
        self.product.save()
        product = {'product': self.product.pk}
        response = self.client.post(reverse('purchasedproduct_add',
                                            kwargs=product),
                                    data=self.purchasedproduct_form_data,
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PurchasedProduct.objects.all().count(), 0)

    def test_purchasedproduct_update(self):
        purchased_product = purchasedproduct_factory(self.product, self.company)
        kwargs = {'pk': purchased_product.pk}

        response = self.client.post(reverse('purchasedproduct_update',
                                            kwargs=kwargs))
        self.assertEqual(response.status_code, 404)

    def test_purchasedproduct_delete(self):
        purchased_product = purchasedproduct_factory(self.product, self.company)
        kwargs = {'pk': purchased_product.pk}

        response = self.client.post(reverse('purchasedproduct_delete',
                                            kwargs=kwargs))
        self.assertEqual(response.status_code, 404)
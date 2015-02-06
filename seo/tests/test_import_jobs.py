# -*- coding: utf-8 -*-
import os

from django.conf import settings

from seo_pysolr import Solr
from import_jobs import DATA_DIR, add_company, remove_expired_jobs, update_solr
from seo.models import BusinessUnit, Company
from seo.tests.factories import BusinessUnitFactory, CompanyFactory
from setup import DirectSEOBase


class ImportJobsTestCase(DirectSEOBase):
    fixtures = ['import_jobs_testdata.json']

    def setUp(self):
        super(ImportJobsTestCase, self).setUp()
        self.businessunit = BusinessUnitFactory(id=0)
        self.buid_id = self.businessunit.id        
        self.filepath = os.path.join(DATA_DIR, 'dseo_feed_%s.xml' % self.buid_id)
        self.solr_settings = {
            'default': {'URL': 'http://127.0.0.1:8983/solr/seo'}
        }
        self.solr = Solr(settings.HAYSTACK_CONNECTIONS['default']['URL'])

    def tearDown(self):
        super(ImportJobsTestCase, self).tearDown()
        self.solr.delete(q='*:*')

    def test_solr_rm_feedfile(self):
        """
        Test that at the end of Solr parsing, the feed file is deleted.
        
        """
        update_solr(self.buid_id)
        self.assertFalse(os.access(self.filepath, os.F_OK))

    def test_subsidiary_rename(self):
        company1 = CompanyFactory()
        company1.save()
        bu1 = self.businessunit
        bu1.title = "Acme corp"
        bu2 = BusinessUnitFactory(title=bu1.title)
        bu2.save()
        self.businessunit.company_set.add(company1)

        # Test that a company was created for both business units
        add_company(bu1)
        companies = bu1.company_set.all()
        self.assertEqual(len(companies), 1)
        co = companies[0]
        self.assertEqual(co.name, bu1.title)

        # Add the 2nd business unit
        add_company(bu2)

        # Both units should be attached to that company
        self.assertEqual(bu1.company_set.all()[0], bu2.company_set.all()[0])
        self.assertEqual(bu1.company_set.all().count(), 1) 
        self.assertIn(bu1, co.job_source_ids.all())
        self.assertIn(bu2, co.job_source_ids.all())
        self.assertEqual(co.name, bu1.title)
        self.assertEqual(co.name, bu2.title)

        bu2.title = "New company name"
        add_company(bu1)
        add_company(bu2)
        self.assertEqual(len(co.job_source_ids.all()), 1)
        self.assertNotEqual(bu1.company_set.all(), bu2.company_set.all())
        self.assertEqual(co.name, bu1.title)
        self.assertEqual(len(bu2.company_set.all()), 1)
        co2 = bu2.company_set.all()[0]
        self.assertEqual(co2.name, bu2.title)
        self.assertNotEqual(co2.name, bu1.title)
        self.assertNotEqual(co.name, bu2.title)

    def test_duplicate_company(self):
        company1 = CompanyFactory()
        company1.save()
        company2 = CompanyFactory(name="Acme corp")
        company2.save()
        self.businessunit.company_set.add(company1)
        self.businessunit.title = "Acme corp"
        add_company(self.businessunit)
        self.assertEqual(self.businessunit.company_set.all()[0], company2)

    def test_set_bu_title(self):
        """
        Ensure that if a feedfile for a BusinessUnit comes through, and
        the `title` attribute for that BusinessUnit is not set, that
        `helpers.update_solr` sets the `title` attribute properly.

        """
        bu = BusinessUnit.objects.get(id=self.buid_id)
        bu.title = None
        bu.save()
        # Since the BusinessUnit title is None, the intent is that update_solr
        # will set its title to match the company name found in the feed file.
        results = update_solr(self.buid_id)
        # We have to get the updated state of the BusinessUnit instance, since
        # changes to the database won't be reflected by our in-memory version of
        # the data.
        bu = BusinessUnit.objects.get(id=self.buid_id)
        # The title attribute should now equal the initial value established in
        # the setUp method.
        self.assertEquals(self.businessunit.title, bu.title)

    def test_add_company(self):
        """
        Create environment to test for every possible case--
        
         - Existing relationship but the name is different                 pk=10
         - No existing relationship, but the company exists in the database (as
           established by the BusinessUnit title matching a company name)  pk=11
         - No relationship and the company is not in the database          pk=12
          
        Start with  2 Company objects and 3 BusinessUnit objects
        End up with 3 Company objects and 3 BusinessUnit objects

        """

        for i in range(10, 4):
            add_company(BusinessUnit.get(id=i))

            # The names of the BU and the Co should be the same
            self.assertEquals(BusinessUnit.get(id=i).title,
                              Company.get(id=i).name,
                              msg="Company names do not match")

            # ensure the relationship was formed
            self.assertIn(Company.objects.get(id=i),
                          BusinessUnit.objects.get(id=i).company_set.all(),
                          msg="Company is not related to job feed")

    def test_remove_expired_jobs(self):
        buid = 12345
        active_jobs = [{'id': 'seo.%s' % i, 'buid': buid} for i in range(4)]
        old_jobs = [{'id': 'seo.%s' % i, 'buid': buid} for i in range(2, 10)]

        with self.settings(HAYSTACK_CONNECTIONS=self.solr_settings):
            self.solr.add(old_jobs)
            self.solr.commit()

            removed = remove_expired_jobs(buid, active_jobs)
            self.assertEqual(len(removed), 6, "Removed jobs %s" % removed)
            ids = [d['id'] for d in self.solr.search('*:*').docs]
            self.assertTrue([5, 6, 7, 8, 9, 10] not in ids)

from django.conf import settings

from seo.tests.factories import UserFactory, BusinessUnitFactory, SeoSiteFactory
from seo.models import BusinessUnit
from setup import DirectSEOBase


class UpdatesTests(DirectSEOBase):
    def setUp(self):
        self.user = UserFactory()
        self.key = settings.BUID_API_KEY
        self.existing_bu = BusinessUnitFactory()

    def test_key(self):
        resp = self.client.get('/ajax/update_buid/')
        self.assertEqual(resp.status_code, 401)

        bad_key = 'zzzz'
        resp = self.client.get('/ajax/update_buid/?key=%s' % bad_key)
        self.assertEqual(resp.status_code, 401)

        resp = self.client.get('/ajax/update_buid/?key=%s' % self.key)
        self.assertEqual('{"error": "Invalid format for old business unit."}',
                         resp.content)

    def test_no_new_buid(self):
        url = '/ajax/update_buid/?key=%s&old_buid=%s' % (self.key,
                                                         self.existing_bu.id)
        resp = self.client.get(url)
        self.assertEqual('{"error": "Invalid format for new business unit."}',
                         resp.content)

    def test_existing_buid(self):
        url = '/ajax/update_buid/?key=%s&old_buid=%s&new_buid=%s' % (self.key,
                                                                     self.existing_bu.id,
                                                                     self.existing_bu.id)
        resp = self.client.get(url)
        self.assertEqual('{"error": "New business unit already exists."}',
                         resp.content)

    def test_no_old_buid(self):
        url = '/ajax/update_buid/?key=%s&new_buid=%s' % (self.key,
                                                         '57')
        resp = self.client.get(url)
        self.assertEqual('{"error": "Invalid format for old business unit."}',
                         resp.content)

    def test_new_buid(self):
        site = SeoSiteFactory()
        site.business_units.add(self.existing_bu)
        site.save()

        url = '/ajax/update_buid/?key=%s&old_buid=%s&new_buid=%s' % (self.key,
                                                                     self.existing_bu.id,
                                                                     105)
        resp = self.client.get(url)
        self.assertEqual('{"new_bu": "105", "sites": "buckconsultants.jobs"}',
                         resp.content)
        buid = BusinessUnit.objects.get(pk=105)
        self.assertTrue(buid.enable_markdown)

    def test_invalid_buid_format(self):
        url = '/ajax/update_buid/?key=%s&new_buid=%s' % (self.key,
                                                         'bad_old_buid')
        resp = self.client.get(url)
        self.assertEqual('{"error": "Invalid format for old business unit."}',
                         resp.content)

        url = '/ajax/update_buid/?key=%s&old_buid=%s&new_buid=%s' % (self.key,
                                                                     self.existing_bu.id,
                                                                     'bad_new_buid')
        resp = self.client.get(url)
        self.assertEqual('{"error": "Invalid format for new business unit."}',
                         resp.content)
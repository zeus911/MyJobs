from seo.models import SeoSite, User

from tastypie.models import ApiKey
from seo.tests.setup import DirectSEOTestCase

from tastypie.serializers import Serializer


class ApiTestCase(DirectSEOTestCase):
    fixtures = ['seo_views_testdata.json']
    def setUp(self):
        super(ApiTestCase, self).setUp()
        # Create a test user and an API key for that user.
        self.user, created = User.objects.create_user(email='test@test.com',
                                                      password='password')
        self.username = self.user.email
        self.user.save()
        self.key = ApiKey(user=self.user)
        self.key.save()
        self.api_key = self.key.key
        self.auth_qs = '?&username=%s&api_key=%s' % (self.username,
                                                     self.api_key)
        self.entry_1 = SeoSite.objects.get(group=1)
        self.detail_url = '/api/v1/seosite/{0}/'.format(self.entry_1.pk)
        self.serializer = Serializer()

    def deserialize(self, resp):
        return self.serializer.deserialize(resp.content, format=resp['Content-Type'])
        
    def test_not_authorized(self):
        """
        Test if a user can gain access without an API key
        """
        user, created = User.objects.create_user(email='someguy@test.com',
                                                 password='password')
        self.username = self.user.email
        user.save()
        resp = self.client.get("api/v1/jobsearch/?format=xml")
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get("api/v1/seosite/?format=xml")
        self.assertEqual(resp.status_code, 404)
        key = ApiKey(user=self.user)
        
    def test_list_xml(self):
        resp = self.client.get("/api/v1/seosite/?%s&format=xml" % (self.auth_qs))
        self.assertEqual(resp.status_code, 200)
        self.serializer.from_xml(resp.content)
        
    def test_list_json(self):
        resp = self.client.get("/api/v1/seosite/?%s&format=json" % (self.auth_qs))
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)
        self.assertEqual(resp.status_code, 200)
        self.serializer.from_json(resp.content)
        
    def test_get_detail_json(self):
        resp = self.client.get("/api/v1/seosite/1/%s&format=json" % (self.auth_qs))
        self.assertEqual(resp.status_code, 200)
        self.serializer.from_json(resp.content)
        self.assertEqual(sorted(self.deserialize(resp).keys()),
                        sorted(['ats_source_codes','business_units',
                                'special_commitments','google_analytics',
                                'site_title', 'resource_uri',
                                'billboard_images', 'group', 'name',
                                'view_sources', 'facets', 'site_heading',
                                'domain', 'site_description','id',
                                'configurations']))
        self.assertEqual(self.deserialize(resp)['name'], 'Test')


    def test_get_detail_xml(self):
        resp = self.client.get("/api/v1/seosite/1/%s&format=xml" % (self.auth_qs))
        self.assertEqual(resp.status_code, 200)
        self.serializer.from_xml(resp.content)

    def test_nopost(self):
        """
        Ensure that POST requests are rejected. This test can be removed
        if/when we allow other methods besides GET to our resources.
        
        """
        jobjson = ("""{"buid": 13543, "city": "Chester",\
                   "company": "Edward Jones", "country": "United States",\
                   "date_new": "2012-05-31T11:49:23",\
                   "mocs": "[\'021\', \'0193\', \'2820\', \'2G000\', \'2G091\',\
                   \'2R000\', \'2R071\', \'2R090\', \'2R171\', \'2S000\',\
                   \'2S071\', \'2S091\', \'2T000\', \'2T071\', \'2T091\',\
                   \'3A000\', \'3A071\', \'3A091\', \'3C000\', \'3C071\',\
                   \'3C090\', \'3C171\', \'3C191\', \'4A000\', \'4A091\',\
                   \'4A100\', \'4A191\', \'6F000\', \'6F091\', \'8M000\']",\
                   "onet": "43101100",\
                   "resource_uri": "/seo/v1/jobposting/29068157/",\
                   "state": "Virginia", "title": "Branch Office Administrator -\
                   Chester, VA - Branch 48113", "uid": "29068157"}""")
        resp = self.client.post("/api/v1/jobsearch/%s" % self.auth_qs,
                                data=jobjson, content_type="application/json")
        # HTTP 405 == 'Method Not Allowed'
        self.assertEqual(resp.status_code, 405)

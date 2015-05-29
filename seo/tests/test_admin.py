from myjobs.models import User
from seo.tests.setup import DirectSEOBase


admin_seo_links = ["atssourcecode",
                   "billboardimage",
                   "businessunit",
                   "company",
                   "configuration",
                   "customfacet",
                   "custompage",
                   "googleanalytics",
                   "googleanalyticscampaign",
                   "seositefacet",
                   "seosite",
                   "specialcommitment",
                   "viewsource"]


class SeoAdminTestCase(DirectSEOBase):
    def setUp(self):
        super(SeoAdminTestCase, self).setUp()
        self.password = 'imbatmancalifornia'
        self.user = User.objects.create_superuser(password=self.password,
                                                  email='bc@batyacht.com')
        self.user.save()
        self.client.login(email=self.user.email,
                          password=self.password)

    def test_add(self):
        """Tests seo admin add views"""
        for link in admin_seo_links:
            resp = self.client.get('/admin/seo/%s/add/' % link)
            self.assertEqual(resp.status_code, 200)

    def test_change(self):
        """Tests seo admin list views"""
        for link in admin_seo_links:
            resp = self.client.get('/admin/seo/%s/' % link)
            self.assertEqual(resp.status_code, 200)
from seo.tests import factories
from seo.tests.setup import DirectSEOBase


class BreadboxTests(DirectSEOBase):
    def setUp(self):
        super(BreadboxTests, self).setUp()
        self.custom_facet_1 = None
        self.custom_facet_2 = None
        self.custom_facet_3 = None
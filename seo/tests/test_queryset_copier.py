from postajob.tests.factories import SitePackageFactory
from seo import models, queryset_copier
from seo.tests.setup import DirectSEOBase
from seo.tests import factories


class QuerysetCopier(DirectSEOBase):
    multi_db = True

    def setUp(self):
        super(QuerysetCopier, self).setUp()
        self.copy_to = 'qc-redirect'

        # Using Company for the object being copied because it covers
        # most types of recursive relationships, foreign keys and
        # many to many relationships.
        self.company = factories.CompanyFactory()
        factories.CompanyUserFactory(company=self.company)

        # copy_objects() expects a queryset
        self.companies = models.Company.objects.filter(pk=self.company.pk)

        self.site_package = SitePackageFactory(owner=self.company)
        self.company.site_package = self.site_package

        self.company.save()

    def test_copy_new_object(self):
        queryset_copier.copy_following_relationships(self.companies)

    def test_copy_update_object(self):
        queryset_copier.copy_following_relationships(self.companies)


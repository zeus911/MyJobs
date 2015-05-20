from django.contrib.auth.models import Group

from seo import models
from seo import queryset_copier as qc
from seo.tests.setup import DirectSEOBase
from seo.tests import factories


class QuerysetCopier(DirectSEOBase):
    multi_db = True

    def setUp(self):
        super(QuerysetCopier, self).setUp()
        self.copy_to = 'qc-redirect'

        # Using SeoSite for the object being copied because it covers
        # most types of recursive relationships, foreign keys and
        # many to many relationships.
        self.obj = factories.SeoSiteFactory(domain='qccopiertest.jobs')

        # copy_objects() expects a queryset
        self.queryset = models.SeoSite.objects.filter(pk=self.obj.pk)

        self.foreign_key_field_names = ['site_ptr']
        self.null_foreign_key_field_names = ['group']
        self.many_to_many_field_names = ['']

    def confirm_copy(self, new_obj):
        for field in self.foreign_key_field_names:
            fk_obj = getattr(self.obj, field)
            new_fk_obj = getattr(new_obj, field)
            self.assertEqual(fk_obj.pk, new_fk_obj.pk)

    def test_copy_new_object(self):
        queue = qc.copy_following_relationships(self.queryset, copy_to=self.copy_to)

        query_base = models.SeoSite.objects.using(self.copy_to)
        new_obj = query_base.get(pk=self.obj.pk)

        self.confirm_copy(new_obj)

    def test_copy_update_object(self):
        qc.copy_following_relationships(self.queryset, copy_to=self.copy_to)


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
        self.seosite = factories.SeoSiteFactory(domain='qccopiertest.jobs')

        # copy_objects() expects a queryset
        self.seosites = models.SeoSite.objects.filter(pk=self.seosite.pk)

        # Many-to-manys
        tag = models.SiteTag.objects.create(site_tag='Copy Test')
        self.seosite.site_tags.add(tag)
        buid = factories.BusinessUnitFactory(pk=123321)
        self.seosite.business_units.add(buid)
        company = factories.CompanyFactory()
        self.seosite.featured_companies.add(company)

        # Nullable Foreign Keys
        self.seosite.canonical_company = company

        self.seosite.save()

        self.site_foreign_key_field_names = ['site_ptr']
        self.site_null_foreign_key_field_names = ['group', 'canonical_company']
        self.site_many_to_many_field_names = ['site_tags', 'business_units',
                                              'featured_companies']

    def confirm_complete(self, queue):
        statuses = [entry[1]['status'] for entry in queue.items()]
        self.assertNotIn(qc.NOT_STARTED, statuses)

    def confirm_copy(self, obj, new_obj, foreign_key_field_names,
                     null_foreign_key_field_names, many_to_many_field_names):
        for field in foreign_key_field_names:
            fk_obj = getattr(obj, field)
            new_fk_obj = getattr(new_obj, field)
            self.assertEqual(fk_obj.pk, new_fk_obj.pk)

        for field in null_foreign_key_field_names:
            fk_obj = getattr(obj, field)
            new_fk_obj = getattr(new_obj, field)
            self.assertEqual(fk_obj.pk, new_fk_obj.pk)

        for field in many_to_many_field_names:
            m2m_objs = getattr(obj, field).values_list('pk', flat=True)
            new_m2m_objs = getattr(new_obj, field).values_list('pk', flat=True)

            self.assertItemsEqual(m2m_objs, new_m2m_objs)

    def test_copy_new_object(self):
        """
        Objects that didn't exist in the copy_to database should be
        correctly be copied from the default database to the copy_to
        database.

        """
        queue = qc.copy_following_relationships(self.seosites, copy_to=self.copy_to)

        self.confirm_complete(queue)

        query_base = models.SeoSite.objects.using(self.copy_to)
        new_seosite = query_base.get(pk=self.seosite.pk)

        self.confirm_copy(self.seosite, new_seosite,
                          self.site_foreign_key_field_names,
                          self.site_null_foreign_key_field_names,
                          self.site_many_to_many_field_names)

        # Do a sanity check to confirm that they really are seperate objects.
        new_seosite.domain = 'updatedseosite.jobs'
        # It knows what db it came from.
        new_seosite.save()
        seosite = models.SeoSite.objects.get(pk=self.seosite)
        self.assertNotEqual(new_seosite.domain, seosite)

    def test_copy_update_object(self):
        """
        Objects that already existed in the copy_to dabase should be
        correctly overwritten in the copy_to database using the data
        from the default database.

        """
        queue = qc.copy_following_relationships(self.seosites, copy_to=self.copy_to)

        self.confirm_complete(queue)

        query_base = models.SeoSite.objects.using(self.copy_to)
        new_obj = query_base.get(pk=self.seosite.pk)

        self.confirm_copy(self.seosite, new_obj,
                          self.site_foreign_key_field_names,
                          self.site_null_foreign_key_field_names,
                          self.site_many_to_many_field_names)


from seo import models
from seo import queryset_copier as qc
from seo.tests.setup import DirectSEOBase
from seo.tests import factories


class QuerysetCopier(DirectSEOBase):
    multi_db = True

    def setUp(self):
        super(QuerysetCopier, self).setUp()
        self.copy_to = factories.copy_to_database

        # Using SeoSite for the object being copied because it covers
        # most types of recursive relationships, foreign keys and
        # many to many relationships.
        self.seosite = factories.SeoSiteFactory()

        # copy_objects() expects a queryset
        self.seosites = models.SeoSite.objects.filter(pk=self.seosite.pk)

        # Many-to-manys
        tag = models.SiteTag.objects.create(site_tag='Copy Test')
        self.seosite.site_tags.add(tag)
        tag = models.SiteTag.objects.create(site_tag='Copy Test 2')
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
            if fk_obj:
                self.assertEqual(fk_obj.pk, new_fk_obj.pk)
            else:
                self.assertIsNone(fk_obj)
                self.assertIsNone(new_fk_obj)

        for fieldname in many_to_many_field_names:
            field = obj.__class__._meta.get_field_by_name(fieldname)[0]
            m2m_objs = qc.get_many_to_many_objects_for_field(obj, field)
            m2m_objs = m2m_objs.values_list('pk', flat=True)

            new_m2m_objs = qc.get_many_to_many_objects_for_field(new_obj, field)
            new_m2m_objs = new_m2m_objs.values_list('pk', flat=True)

            self.assertItemsEqual(m2m_objs, new_m2m_objs,
                                  msg="M2M not equal for field %s. "
                                      "Old object had %s, new object had "
                                      "%s."
                                      % (fieldname, m2m_objs, new_m2m_objs))

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
        factories.SeoSiteCopyToFactory(id=self.seosite.pk)

        # Confirm we're working with two different objects.
        site = models.SeoSite.objects.get(pk=self.seosite)
        query_base = models.SeoSite.objects.using(self.copy_to)
        copied_site = query_base.get(pk=self.seosite)
        self.assertNotEqual(site.domain, copied_site.domain)

        queue = qc.copy_following_relationships(self.seosites, copy_to=self.copy_to)

        self.confirm_complete(queue)

        new_obj = query_base.get(pk=self.seosite.pk)
        self.confirm_copy(self.seosite, new_obj,
                          self.site_foreign_key_field_names,
                          self.site_null_foreign_key_field_names,
                          self.site_many_to_many_field_names)

        # Confirm the object has been updated in the self.copy_to database.
        site = models.SeoSite.objects.get(pk=self.seosite)
        query_base = models.SeoSite.objects.using(self.copy_to)
        copied_site = query_base.get(pk=self.seosite)
        self.assertEqual(site.domain, copied_site.domain)

import django.core.cache
import django.utils.cache

from mock import patch, Mock

import middleware
from seo import cache
from seo import models
from seo.tests.setup import DirectSEOTestCase, patch_settings
from seo.tests import factories
from seo.views import search_views as views
from seo.templatetags import seo_extras


class LocalCacheTestCase(DirectSEOTestCase):
    fixtures = ['seo_views_testdata.json']

    def setUp(self):
        super(LocalCacheTestCase, self).setUp()
        self.locmem_cache = django.core.cache.get_cache(
                'django.core.cache.backends.locmem.LocMemCache')
        self.locmem_cache.clear()
        # All modules that imports cache needs to be patched
        # to use our local memcache. Modules imported with different
        # namespaces need multiple patches
        self.cache_modules = [django.core.cache, 
                              models,
                              cache,
                              views,
                              seo_extras,
                              middleware]
        self.cache_patches = []
        for module in self.cache_modules:
            self.cache_patches.append(patch.object(module, 'cache', self.locmem_cache))
        for cache_patch in self.cache_patches:
            cache_patch.start()
        get_cache_patch = patch.object(django.core.cache, 'get_cache', 
                                       Mock(return_value=self.locmem_cache))

    def tearDown(self):
        super(DirectSEOTestCase, self).tearDown()
        for cache_patch in self.cache_patches:
            cache_patch.stop()

    def test_expire_site_on_config_save(self):
        """
        Cache pages and site-related objects should be cleared when its config is saved

        """
        with patch_settings(CACHES = {'default': {'BACKEND':
            'django.core.cache.backends.locmem.LocMemCache'}}):

            # Build a site with billboard images to check the billboard's
            # caching behavior as well
            site = factories.SeoSiteFactory.build(domain='oranges.jobs')
            site.save()
            config = factories.ConfigurationFactory.build(status=2, home_page_template='home_page/home_page_static_header_footer.html')
            config.meta = 'initial meta'
            config.save()
            site.configurations = [config]

            response = self.client.get('/',
                                       HTTP_HOST=u'oranges.jobs')
            self.assertContains(response, config.meta)

            # Update config without calling save()
            config.meta = 'new meta'
            models.Configuration.objects.filter(id=config.id).update(
                meta=config.meta)
            response = self.client.get('/',
                                       HTTP_HOST=u'oranges.jobs')

            # Old config should still be cached
            self.assertContains(response, 'initial meta')
            self.assertNotContains(response, config.meta)
            config.save()

            response = self.client.get('/',
                                       HTTP_HOST=u'oranges.jobs')

            config.save()
            self.assertContains(response, config.meta) 
            self.assertNotContains(response, 'initial meta')

    def test_expire_site_on_save(self):
        """
        Cache pages and site-related objects should be cleared when an SeoSite
        is saved.

        """
        with patch_settings(CACHES = {'default': {'BACKEND':
            'django.core.cache.backends.locmem.LocMemCache'}}):

            # Build a site with billboard images to check the billboard's
            # caching behavior as well
            site = factories.SeoSiteFactory.build(site_title='Initial Title')
            site.save()
            config = factories.ConfigurationFactory.build(status=2,
                    show_home_microsite_carousel=True)
            config.save()
            site.configurations = [config]
            billboard = factories.BillboardImageFactory.build(image_url="http://initial_url")
            billboard.save()
            site.billboard_images.add(billboard)

            response = self.client.get('/',
                                       HTTP_HOST=u'buckconsultants.jobs')
            self.assertNotEqual(response.context['default_jobs'], 0)
            self.assertNotEqual(response.content.find('Initial Title'), -1)
            self.assertNotEqual(response.content.find(billboard.image_url), -1)

            # Make changes to the site instance and database without calling save()
            models.SeoSite.objects.filter(id=site.id).update(site_title='Updated Title')
            site.site_title = 'Updated Title'
            site.configurations.all().update(header=
                                             'Unique Header')
            billboard.image_url = 'http://updated_url'
            site.billboard_images.update(image_url=billboard.image_url)

            # This response should still be cached and not reflect the site changes
            response = self.client.get('/',
                                       HTTP_HOST=u'buckconsultants.jobs')
            # Cached pages don't return a context
            self.assertEqual(response.context, None)
            self.assertNotEqual(response.content.find('Initial Title'), -1)
            self.assertEqual(response.content.find('Updated Title'), -1)
            self.assertEqual(response.content.find('Unique Header'), -1)
            self.assertNotEqual(response.content.find('http://initial_url'), -1)
            self.assertEqual(response.content.find('http://updated_url'), -1)

            billboard.save()
            site.save()

            response = self.client.get('/?q=foo',
                                       HTTP_HOST=u'buckconsultants.jobs')
            # This page isn't cached, confirm that our model caching has cleared
            # on site save
            self.assertNotEqual(response.content.find('Updated Title'), -1)
            self.assertNotEqual(response.content.find(billboard.image_url), -1)
            self.assertNotEqual(response.content.find('Unique Header'), -1)
            response = self.client.get('/',
                                       HTTP_HOST=u'buckconsultants.jobs')

            # The cache is cleared and the home_page should be updated 
            self.assertNotEqual(response.context['default_jobs'], 0)
            self.assertNotEqual(response.content.find('Updated Title'), -1)
            self.assertNotEqual(response.content.find(billboard.image_url), -1)
            self.assertNotEqual(response.content.find('Unique Header'), -1)

            no_job_buid = factories.BusinessUnitFactory.build(id=562)
            no_job_buid.save()
            site.business_units = [no_job_buid]

            site.save()

            # One buid with no jobs attached to the site
            response = self.client.get('/',
                                       HTTP_HOST=u'buckconsultants.jobs')
            # Should be no jobs returned
            self.assertNotEqual(response.context, None)
            self.assertEqual(len(response.context['default_jobs']), 0)

            site.business_units.add(self.businessunit)
            site.save()

            # Cache should be refreshed and this buid should return jobs
            response = self.client.get('/',
                                       HTTP_HOST=u'buckconsultants.jobs')
            self.assertNotEqual(response.context, None)
            self.assertTrue(len(response.context['default_jobs']) > 0)

            # Saving a configuration should clear the cache
            site.configurations.all().update(header=
                                             'Yet Another Header')
            site.configurations.all()[0].save()

            response = self.client.get('/',
                                       HTTP_HOST=u'buckconsultants.jobs')
            self.assertNotEqual(response.context, None)
            self.assertTrue(len(response.context['default_jobs']) > 0)
            self.assertNotEqual(response.content.find('Yet Another Header'), -1)

from slugify import slugify

from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from myjobs.tests.factories import UserFactory
from seo.models import BusinessUnit, Configuration, SeoSite, SiteTag
from seo.tests.factories import (BusinessUnitFactory, CustomFacetFactory,
                                 SeoSiteFacetFactory, SpecialCommitmentFactory)
from seo.tests.setup import DirectSEOBase
from seo.tests.solr_settings import SOLR_FIXTURE
from universal.helpers import build_url


class BlocksTestBase(DirectSEOBase):
    def setUp(self):
        super(BlocksTestBase, self).setUp()
        self.site = SeoSite.objects.get()
        self.config = Configuration.objects.get(status=2)
        self.config.browse_facet_show = True
        self.config.save()

        # Can't do a get_or_create here because we don't
        # care about the date_crawled/date_updated fields,
        # but if the BusinessUnit doesn't exist they will need
        # to be supplied.
        try:
            self.buid = BusinessUnit.objects.get(pk=0)
        except BusinessUnit.DoesNotExist:
            self.buid = BusinessUnitFactory(id=0)

        self.site.business_unit.add(0)

        self.commitment = SpecialCommitmentFactory()
        self.site.special_commitments.add(self.commitment)
        self.site.save()

        self.tag = SiteTag.objects.create(site_tag='Test tag')
        self.site.site_tags.add(self.tag)
        self.site.save()

        self.job = SOLR_FIXTURE[1]
        self.conn.add([self.job])

        self.user = UserFactory()

        url = reverse('all_jobs')
        self.search_results_request = RequestFactory().get(url)
        self.search_results_request.user = self.user

        self.q_kwargs = {'q': self.job['title']}
        url = build_url(reverse('all_jobs'), self.q_kwargs)
        self.search_results_with_q_request = RequestFactory().get(url)
        self.search_results_with_q_request.user = self.user

        self.facet = CustomFacetFactory(show_production=True,
                                        name='%s' % self.job['title'],
                                        name_slug='%s' % self.job['title_slug'],
                                        querystring='*',
                                        blurb='Test')
        self.bad_facet = CustomFacetFactory(show_production=True,
                                            name='Bad Facet',
                                            name_slug='bad-facet',
                                            querystring='asfljasdlfjsadfsdf',
                                            blurb='Test',
                                            always_show=True)
        SeoSiteFacetFactory(customfacet=self.facet, seosite=self.site)
        SeoSiteFacetFactory(customfacet=self.bad_facet, seosite=self.site)

        url = '%s/new-jobs/' % self.job['title_slug']
        self.search_results_with_custom_facet = RequestFactory().get(url)
        self.search_results_with_custom_facet.user = self.user

        self.job_detail_kwargs = {
            'job_id': self.job['guid'],
            'title_slug': self.job['title_slug'],
            'location_slug': slugify(self.job['location']),
        }
        url = reverse('job_detail_by_location_slug_title_slug_job_id',
                      kwargs=self.job_detail_kwargs)
        self.job_detail_request = RequestFactory().get(url)
        self.job_detail_request.user = self.user

        kwargs = {'job_id': self.job['guid']}
        url = reverse('job_detail_by_job_id', kwargs=kwargs)
        self.job_detail_redirect_request = RequestFactory().get(url)
        self.job_detail_redirect_request.user = self.user

        # Send a request through middleware so all the required
        # settings (from MultiHostMiddleware) actually get set.
        self.client.get('/')
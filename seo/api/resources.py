import operator

from tastypie.authentication import ApiKeyAuthentication
from tastypie.resources import *
from tastypie.utils import trailing_slash

from api.resources import SearchResource
from api.throttle import SmartCacheDBThrottle
from seo.search_backend import DESearchQuerySet
from seo.models import (ATSSourceCode, BillboardHotspot, BillboardImage,
                        BusinessUnit, Company, Configuration, CustomFacet,
                        FeaturedCompany, GoogleAnalytics,
                        GoogleAnalyticsCampaign, SeoSite, SpecialCommitment,
                        ViewSource)
from moc_coding.models import Moc, MocDetail, Onet

from django.contrib.auth.models import Group


class ViewSourceResource(ModelResource):
    class Meta:
        queryset = ViewSource.objects.all()
        resource_name = 'view_source'
        filtering = {
            'name': ALL,
            'view_source': ALL
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()

        
class GroupResource(ModelResource):
    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'
        filtering = {
            'name': ALL,
            'id': ALL
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()

        
class ATSResource(ModelResource):
    group = fields.ForeignKey(GroupResource, 'group', null=True)
    class Meta:
        queryset = ATSSourceCode.objects.all()
        resource_name = 'ats_source_code'
        filtering = {
            'ats_name': ALL,
            'name': ALL,
            'value': ALL,
            'group': ALL_WITH_RELATIONS
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()
        
        
class BusinessUnitResource(ModelResource):
    class Meta:
        queryset = BusinessUnit.objects.all()
        resource_name = 'business_unit'
        filtering = {
            'title': ALL,
            'title_slug': ALL,
            'data_crawled': ALL,
            'date_updated': ALL,
            'associated_jobs': ALL,
            'federal_contractor':ALL,
            'id':ALL
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()


class GoogleAnalyticsResource(ModelResource):
    class Meta:
        queryset = GoogleAnalytics.objects.all()
        resource_name = 'google_analytics'
        filtering = {
            'web_property_id': ALL,
            'group': ALL_WITH_RELATIONS,
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()


class GoogleAnalyticsCampaignResource(ModelResource):
    group = fields.ForeignKey(GroupResource, 'group', null=True)
    class Meta:
        queryset = GoogleAnalyticsCampaign.objects.all()
        resource_name = 'google_analytics_campaign'
        filtering = {
            'name': ALL,
            'group': ALL_WITH_RELATIONS,
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()

        
class SpecialCommitmentResource(ModelResource):
    class Meta:
        queryset = SpecialCommitment.objects.all()
        resource_name = 'special_commitment'
        filtering = {
            'name': ALL,
            'commit': ALL
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()

        
class ConfigurationResource(ModelResource):
    class Meta:
        queryset = Configuration.objects.all()
        resource_name = 'configuration'
        filtering = {
            'title': ALL,
            'status': ALL,
            'group': ALL_WITH_RELATIONS,
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()
        

class BillboardImageResource(ModelResource):
    group = fields.ForeignKey(GroupResource, 'group', null=True)
    class Meta:
        queryset = BillboardImage.objects.all()
        resource_name = 'billboard_image'
        filtering = {
            'title': ALL,
            'group': ALL_WITH_RELATIONS,
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()

        
class CustomFacetResource(ModelResource):
    group = fields.ForeignKey(GroupResource, 'group', null=True)
    business_units = fields.ToManyField(BusinessUnitResource, 'business_units',
                                        blank=True, null=True)
    class Meta:
        queryset = CustomFacet.objects.all()
        resource_name = 'custom_facet'
        filtering = {
            'group': ALL_WITH_RELATIONS,
            'business_units': ALL_WITH_RELATIONS,
            'country': ALL,
            'state': ALL,
            'city': ALL,
            'keyword': ALL,
            'onet': ALL,
            'always_show': ALL
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()
        

class SeoSiteResource(ModelResource):
    view_sources = fields.ForeignKey(ViewSourceResource, 'view_sources',null=True,
                                     full=True)
    ats_source_codes = fields.ToManyField(ATSResource, 'ats_source_codes', null=True,
                                          full=True)
    google_analytics = fields.ToManyField(GoogleAnalyticsResource, 'google_analytics',
                                          null=True,full=True)
    business_units = fields.ToManyField(BusinessUnitResource, 'business_units',
                                        null=True,full=True)
    special_commitments = fields.ToManyField(SpecialCommitmentResource,
                                             'special_commitments', null=True,
                                             full=True)
    facets = fields.ToManyField(CustomFacetResource, 'facets', null=True, blank=True)
    configurations = fields.ToManyField(ConfigurationResource, 'configurations',
                                        null=True,blank=True)
    billboard_images = fields.ToManyField(BillboardImageResource, 'billboard_images',
                                           blank=True,null=True)
    group = fields.ForeignKey(GroupResource, 'group', null=True)
    
    class Meta:
        queryset = SeoSite.objects.all()
        resource_name = 'seosite'
        filtering = {
            'group': ALL_WITH_RELATIONS,
            'business_units': ALL_WITH_RELATIONS,
            'ats_source_codes': ALL_WITH_RELATIONS,
            'view_sources': ALL_WITH_RELATIONS,
            'google_analytics': ALL_WITH_RELATIONS,
            'special_commitments': ALL_WITH_RELATIONS,
            'facets': ALL_WITH_RELATIONS,
            'configurations': ALL_WITH_RELATIONS,
            'id':ALL,
            'domain': ALL,
        }
        authentication = ApiKeyAuthentication()

        
class CompanyResource(ModelResource):
    class Meta:
        queryset = Company.objects.all()
        resource_name = 'company'
        filtering = {
            'name': ALL,
            'company_slug': ALL,
            'member': ALL,
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()


class FeaturedCompanyResource(ModelResource):
    seosite = fields.ForeignKey(SeoSiteResource, 'seosite')
    company = fields.ForeignKey(Company, 'company')
    class Meta:
        queryset = FeaturedCompany.objects.all()
        resource_name = 'featured_company'
        filtering = {
            'seosite': ALL_WITH_RELATIONS,
            'company': ALL_WITH_RELATIONS,
            'is_featured': ALL
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()


class BillboardHotspotResource(ModelResource):
    billboard_image = fields.ForeignKey(BillboardImageResource, 'billboard_image')
    class Meta:
        queryset = BillboardHotspot.objects.all()
        resource_name = 'billboard_hotspot'
        filtering = {
            'billboard_image': ALL_WITH_RELATIONS,
            'title': ALL,
            'text': ALL,
            'url': ALL
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()


class OnetResource(ModelResource):
    class Meta:
        queryset = Onet.objects.all()
        resource_name = 'onet'
        filtering = {
            'title': ALL,
            'code': ALL
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()        
        

class MocDetailResource(ModelResource):
    class Meta:
        queryset = MocDetail.objects.all()
        resource_name = 'moc_detail'
        filtering = {
            'primary_value': ALL,
            'service_branch': ALL,
            'military_description': ALL,
            'civilian_description': ALL
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()


class MocResource(ModelResource):
    moc_detail = fields.ToOneField(MocDetailResource, 'moc_detail', null=True)
    class Meta:
        queryset = Moc.objects.all()
        resource_name = 'moc'
        filtering = {
            'moc_detail': ALL_WITH_RELATIONS,
            'onets': ALL_WITH_RELATIONS,
            'title-slug': ALL,
            'title': ALL,
            'branch': ALL,
            'code': ALL
        }
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()
    
    
class JobSearchResource(SearchResource):
    field_aliases = {
        'city': 'city__exact',
        'company': 'company__exact',
        'country': 'country__exact',
        'state': 'state__exact',
    }
    buid = fields.IntegerField(attribute='buid', blank=True, null=True)
    city = fields.CharField(attribute='city', blank=True, null=True)
    company = fields.CharField(attribute='company', blank=True, null=True)
    country = fields.CharField(attribute='country', blank=True, null=True)
    date_new = fields.DateField(attribute='date_new', blank=True, null=True)
    mocs = fields.CharField(attribute='moc', blank=True, null=True)
    onet = fields.CharField(attribute='onet', blank=True, null=True)
    state = fields.CharField(attribute='state', blank=True, null=True)
    title = fields.CharField(attribute='title', blank=True, null=True)
    uid = fields.CharField(attribute='uid', blank=True, null=True)
        
    def _build_reverse_url(self, name, args=None, kwargs=None):
        if 'pk' in kwargs:
            return '/seo/%s/%s/%s/' % (kwargs.get('api_name', 'v1'),
                                       self._meta.dispatch_name,
                                       kwargs.get('pk', '0'))
        else:
            return super(JobSearchResource, self)._build_reverse_url(name, args,
                                                                     kwargs)

    def build_filters(self, filters=None):
        terms = []

        if filters is None:
            filters = {}

        for param_alias, value in filters.items():
            
            if param_alias not in self._meta.index_fields:
                continue
            
            param = self.field_aliases.get(param_alias, param_alias)
            tokens = value.split(self._meta.lookup_sep)
            field_queries = []
            
            for token in tokens:
                
                if token:
                    field_queries.append(self._meta.query_object((param,
                                                                  token)))

            terms.append(reduce(operator.or_,
                                filter(lambda x: x, field_queries)))

        if terms:
            return reduce(operator.and_, filter(lambda x: x, terms))
        else:
            return terms
    
    class Meta:
        allowed_methods = ['get']
        resource_name = 'jobsearch'
        object_class = DESearchQuerySet
        document_uid_field = 'uid'
        dispatch_name = 'jobposting'
        index_fields = [
            'buid',
            'city',
            'company',
            'country',
            'date_new',
            'moc',
            'onet',
            'state',
            'title',
            'uid'
        ]
        authentication = ApiKeyAuthentication()
        throttle = SmartCacheDBThrottle()


class JobResource(ModelResource):
    class Meta:
        allowed_methods = ['get']
        authentication = ApiKeyAuthentication()
        resource_name = 'jobposting'
        excludes = [
            'reqid',
            'countrySlug',
            'titleSlug',
            'citySlug',
            'id',
            'hitkey',
            'link',
            'stateSlug',
        ]
        throttle = SmartCacheDBThrottle()

    def base_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name,
                                                trailing_slash()),
                self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name,
                                                       trailing_slash()),
                self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/set/(?P<pk_list>\w[\w/;-]*)/$" %
                self._meta.resource_name, self.wrap_view('get_multiple'),
                name="api_get_multiple"),
            url(r"^(?P<resource_name>%s)/(?P<uid>\w[\w/-]*)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]



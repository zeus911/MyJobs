import hashlib

from django.core.cache import cache
from django.http import HttpRequest
from django.utils.cache import get_cache_key
from seo.helpers import get_jobs, get_solr_facet

from seo.models import Configuration
from django.conf import settings
'''
This module is currently a holding place for low-level caching that was
scattered across different modules. It's not much better than throwing
everything in helpers.py, but it should make refactoring caching easier in the
future.

'''
#Time to cache data affected by regular job updates
MINUTES_TO_CACHE_JOB_DATA = 10 


def cache_page_prefix(request):
    """Returns the key prefix based on the input request"""
    config = get_site_config(request)
    return "%s-%s-%s-%s" % (request.get_host(), config.id,
                            config.status, config.revision)


def expire_site_view(host, path):
    request = HttpRequest(host=host)
    request.path = path
    key = get_cache_key(request, key_prefix=cache_page_prefix)
    if cache.has_key(key):
        cache.delete(key)


def site_item_key(item_key):
    """
    Returns a key to cache an object
    Input:
        :item_key: A string to uniquely identify the cached item within a site

    """
    return "%s::%s" % (item_key, settings.SITE_ID)


def get_total_jobs_count():
    """Returns the job count for the current site's default job view"""
    jobs_count_key = site_item_key('jobs_count')
    jobs_count = cache.get(jobs_count_key)
    if not jobs_count:
        jobs_count = get_jobs(custom_facets=settings.DEFAULT_FACET,
                              jsids=settings.SITE_BUIDS).count()
        cache.set(jobs_count_key, jobs_count, MINUTES_TO_CACHE_JOB_DATA*60)
    return jobs_count


def get_facet_count_key(filters=None, query_string=None):
    """
    Returns a unique key for the current site and filter path
    Inputs:
        filters: Filters for the current search. If the unicode
                 representation of two filters is equal, they should represent
                 the same search.
    """
    filters = filters or ''
    query_string = query_string or ''

    #We use a hash to ensure key length is under memcache's 250 character limit
    return "browsefacets::%s%s%s" % (
        settings.SITE_ID,
        hashlib.md5(unicode(filters)).hexdigest(),
        hashlib.md5(unicode(query_string)).hexdigest()
    )


def get_custom_facets(request, filters=None, query_string=None):
    custom_facet_key = get_facet_count_key(filters, query_string)
    custom_facets = cache.get(custom_facet_key)

    if not custom_facets:
        custom_facets = get_solr_facet(settings.SITE_BUIDS, filters=filters,
                                       params=request.GET)
        cache.set(custom_facet_key, custom_facets)

    return custom_facets


def get_site_config(request):
    """
    Returns the currently active site configuration for the input request

    """
    # If the user is logged in/staff and specifying a different domain,
    # allow them to get the config for the requested domain, but don't
    # cache it.
    if request.user.is_staff and 'domain' in request.REQUEST:
        host = request.REQUEST.get('domain')
        try:
            return Configuration.objects.get(status=2, seosite__domain=host)
        except Configuration.DoesNotExist:
            try:
                return Configuration.objects.get(status=1, seosite__domain=host)
            except Configuration.DoesNotExist:
                pass

    # Check if user should see staging/production configuration
    # Status 1 is staging, status 2 is production.
    config_status = 1 if request.user.is_staff else 2
    # Lookup configuration here to determine the cache key prefix, grabbing
    # the configuration from cache if it exists.
    config_cache_key = '%s:config:%s' % (request.get_host(), config_status)
    timeout = 60 * settings.MINUTES_TO_CACHE
    config_cache = cache.get(config_cache_key)
    if config_cache:
        site_config = config_cache
    # If the configuration is not in cache, get it and set it for future
    # requests to this site.
    else:
        if request.user.is_staff:
            try:
                # if you are logged in as staff, try to grab the staging
                # configuration
                site_config = Configuration.this_site.get(status=1)
            except Configuration.DoesNotExist:
                try:
                    # if there is no staging configuration, just grab the
                    # production one
                    site_config = Configuration.this_site.get(status=2)
                except Configuration.DoesNotExist:
                    # neither staging or production configs exist for this
                    # site so go to the
                    # default staging configuration
                    site_config = Configuration.objects.get(id=1)
        elif request.user.is_anonymous:
            try:
                # grab the production configuration if the user isn't logged in
                site_config = Configuration.this_site.get(status=2)
            except Configuration.DoesNotExist:
                # serve the default production configuration
                site_config = Configuration.objects.get(id=2)
        cache.set(config_cache_key, site_config, timeout)
    return site_config

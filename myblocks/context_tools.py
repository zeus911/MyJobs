from itertools import chain

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.functional import memoize

from seo import cache, helpers
from seo.breadbox import Breadbox
from seo.templatetags.job_setup import create_arranged_jobs


_context_cache = {}


def get_arranged_jobs(request):
    featured_jobs = get_featured_jobs(request)
    default_jobs = get_default_jobs(request)
    site_config = get_site_config(request)
    return create_arranged_jobs(request, featured_jobs, default_jobs,
                                site_config)


def get_breadbox(request):
    filters = get_filters(request)
    featured_jobs, default_jobs, facet_counts = get_jobs_and_counts(request)
    jobs = chain(featured_jobs, default_jobs)
    return Breadbox(request.path, filters, jobs, request.GET)


def get_custom_facet_counts(request):
    custom_facet_counts = []
    filters = get_filters(request)
    querystring = get_query_string(request)
    site_config = get_site_config(request)

    if site_config.browse_facet_show:
        cached_custom_facets = cache.get_custom_facets(request, filters=filters,
                                                       query_string=querystring)

        if not filters['facet_slug']:
            custom_facet_counts = cached_custom_facets
        else:
            facet_slugs = filters['facet_slug'].split('/')
            active_facets = helpers.standard_facets_by_name_slug(facet_slugs)
            custom_facet_counts = [(facet, count) for facet, count
                                   in cached_custom_facets
                                   if facet not in active_facets]

    return custom_facet_counts


def get_default_jobs(request):
    default_jobs, _, _ = get_jobs_and_counts(request)
    return default_jobs


def get_featured_jobs(request):
    _, featured_jobs, _ = get_jobs_and_counts(request)
    return featured_jobs


def get_filters(request):
    return helpers.build_filter_dict(request.path)


def get_jobs_and_counts(request):
    filters = get_filters(request)
    site_config = get_site_config(request)
    num_jobs = int(site_config.num_job_items_to_show) * 2
    percent_featured = site_config.percent_featured

    args = (request, filters, num_jobs)
    default_jobs, featured_jobs, facet_counts = helpers.jobs_and_counts(*args)

    args = (featured_jobs.count(), default_jobs.count(), num_jobs,
            percent_featured)
    featured_needed, default_needed, _, _ = helpers.featured_default_jobs(*args)

    default_jobs = default_jobs[:default_needed]
    featured_jobs = featured_jobs[:featured_needed]

    jobs = list(chain(featured_jobs, default_jobs))
    for job in jobs:
        helpers.add_text_to_job(job)

    return default_jobs, featured_jobs, facet_counts


def get_location_term(request):
    breadbox = get_breadbox(request)
    return breadbox.location_display_heading()


def get_moc_term(request):
    breadbox = get_breadbox(request)
    return breadbox.moc_display_heading()


def get_moc_id_term(request):
    return request.GET.get('moc_id', '')


def get_query_string(request):
    return request.META.get('QUERY_STRING', None)


def get_search_url(request):
    return request.path if request.path != '/' else reverse('all_jobs')


def get_site_commitments_string(request):
    return helpers.make_specialcommit_string(settings.COMMITMENTS.all())


def get_site_config(request):
    return cache.get_site_config(request)


def get_title_term(request):
    return request.GET.get('q', '')


def get_total_jobs_count(request):
    return cache.get_total_jobs_count()


def get_widgets(request):
    filters = get_filters(request)
    _, _, facet_counts = get_jobs_and_counts(request)
    site_config = get_site_config(request)

    custom_facet_counts = get_custom_facet_counts(request)

    return helpers.get_widgets(request, site_config, facet_counts,
                               custom_facet_counts, filters=filters)

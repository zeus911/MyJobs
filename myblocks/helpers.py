import itertools
from HTMLParser import HTMLParser

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.cache import cache
from django.utils.html import strip_tags


from xmlparse import text_fields
from seo.cache import get_facet_count_key, get_site_config, get_total_jobs_count
from seo import helpers
from seo.models import Company, CustomFacet


def get_jobs(request):
    print 'aslkfjafjasdlfjasd'
    filters = helpers.build_filter_dict(request.path)
    query_path = request.META.get('QUERY_STRING', None)

    redirect_url = helpers.determine_redirect(request, filters)
    if redirect_url:
        return redirect_url

    active = []
    facet_blurb = ''
    search_url_slabs = []
    path = "http://%s%s" % (request.META.get('HTTP_HOST', 'localhost'),
                            request.path)
    num_filters = len([k for (k, v) in filters.iteritems() if v])
    moc_id_term = request.GET.get('moc_id', None)
    q_term = request.GET.get('q', None)

    ga = settings.SITE.google_analytics.all()
    sitecommit_str = helpers.make_specialcommit_string(
        settings.COMMITMENTS.all())
    site_config = get_site_config(request)
    num_jobs = int(site_config.num_job_items_to_show) * 2

    sqs = helpers.prepare_sqs_from_search_params(request.GET) if query_path else None
    custom_facets = []

    if site_config.browse_facet_show:
        cust_key = get_facet_count_key(filters, query_path)
        cust_facets = cache.get(cust_key)

        if not cust_facets:
            cust_facets = helpers.get_solr_facet(settings.SITE_ID,
                                                 settings.SITE_BUIDS,
                                                 filters,
                                                 params=request.GET)
            cache.set(cust_key, cust_facets)

        cf_count_tup = cust_facets
        cf_count_tup = helpers.combine_groups(cf_count_tup)

        if not filters['facet_slug']:
            search_url_slabs = [(i[0].url_slab, i[1]) for i in cf_count_tup]
        else:
            for x in cf_count_tup:
                if x[0].name_slug == filters['facet_slug']:
                    if not facet_blurb and x[0].show_blurb:
                        facet_blurb = x[0].blurb
                    active.append(x[0])
                else:
                    search_url_slabs.append((x[0].url_slab, x[1]))
            if active:
                custom_facets = CustomFacet.objects.filter(
                    name=active[0].name,
                    seosite__id=settings.SITE_ID)
                sqs = helpers.sqs_apply_custom_facets(custom_facets, sqs=sqs)
    else:
        custom_facets = settings.DEFAULT_FACET

    default_jobs = helpers.get_jobs(default_sqs=sqs,
                                    custom_facets=settings.DEFAULT_FACET,
                                    exclude_facets=settings.FEATURED_FACET,
                                    jsids=settings.SITE_BUIDS, filters=filters,
                                    facet_limit=num_jobs)
    jobs_count = get_total_jobs_count()
    featured_jobs = helpers.get_featured_jobs(default_sqs=sqs,
                                              filters=filters,
                                              jsids=settings.SITE_BUIDS,
                                              facet_limit=num_jobs)
    facet_counts = default_jobs.add_facet_count(featured_jobs).get('fields')

    (num_featured_jobs, num_default_jobs, _, _) = helpers.featured_default_jobs(
        featured_jobs.count(), default_jobs.count(),
        num_jobs, site_config.percent_featured)

    # Strip html and markdown formatting from description snippets
    try:
        i = text_fields.index('description')
        text_fields[i] = 'html_description'
    except ValueError:
        pass
    h = HTMLParser()
    all_jobs = itertools.chain(default_jobs[:num_default_jobs],
                               featured_jobs[:num_featured_jobs])
    for job in all_jobs:
        text = filter(None, [getattr(job, x, "None") for x in text_fields])
        unformatted_text = h.unescape(strip_tags(" ".join(text)))
        setattr(job, 'text', unformatted_text)

    bread_box_path = helpers.get_bread_box_path(filters)

    if num_featured_jobs != 0:
        bread_box_title = helpers.get_bread_box_title(filters,
                                                      featured_jobs[:num_featured_jobs])
    else:
        bread_box_title = helpers.get_bread_box_title(filters,
                                                      default_jobs[:num_default_jobs])

    if filters['company_slug']:
        company_obj = Company.objects.filter(member=True).filter(
            company_slug=filters['company_slug'])
        if company_obj:
            company_data = helpers.company_thumbnails(company_obj)[0]
        else:
            company_data = None
    else:
        company_data = None

    if filters['facet_slug'] and active:
        bread_box_title['facet_slug'] = active[0].name

    widgets = helpers.get_widgets(request, site_config, facet_counts,
                                  search_url_slabs, bread_box_path)

    loc_term = bread_box_title.get('location_slug', request.GET.get('location', '\*'))
    moc_term = bread_box_title.get('moc_slug', request.GET.get('moc', '\*'))

    count_heading_dict = bread_box_title.copy()
    count_heading_dict['count'] = intcomma(featured_jobs.count() +
                                           default_jobs.count())
    if loc_term != '\*':
        count_heading_dict['location_slug'] = loc_term

    count_heading = helpers.build_results_heading(count_heading_dict)
    results_heading = helpers.build_results_heading(bread_box_title)

    return {
        'base_path': request.path,
        'bread_box_path': bread_box_path,
        'bread_box_title': bread_box_title,
        'build_num': settings.BUILD,
        'company': company_data,
        'count_heading': count_heading,
        'default_jobs': default_jobs[:num_default_jobs],
        'facet_blurb': facet_blurb,
        'featured_jobs': featured_jobs[:num_featured_jobs],
        'filters': filters,
        'google_analytics': ga,
        'host': str(request.META.get("HTTP_HOST", 'localhost')),
        'location_term': loc_term if loc_term else '\*',
        'max_filter_settings': settings.ROBOT_FILTER_LEVEL,
        'moc_id_term': moc_id_term if moc_id_term else '\*',
        'moc_term': moc_term if moc_term else '\*',
        'num_filters': num_filters,
        'total_jobs_count': jobs_count,
        'results_heading': results_heading,
        'search_url': request.path,
        'site_commitments': settings.COMMITMENTS,
        'site_commitments_string': sitecommit_str,
        'site_config': site_config,
        'site_description': settings.SITE_DESCRIPTION,
        'site_heading': settings.SITE_HEADING,
        'site_name': settings.SITE_NAME,
        'site_tags': settings.SITE_TAGS,
        'site_title': settings.SITE_TITLE,
        'title_term': q_term if q_term else '\*',
        'view_source': settings.VIEW_SOURCE,
        'widgets': widgets,
    }
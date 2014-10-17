from django.core.urlresolvers import reverse


def get_jobs(request):
    return {
        'base_path': '',
        'bread_box_path': '',
        'bread_box_title': '',
        'build_num': '',
        'company': '',
        'count_heading': '',
        'default_jobs': '',
        'facet_blurb': '',
        'featured_jobs': '',
        'filters': '',
        'google_analytics': '',
        'host': '',
        'location_term': '',
        'max_filter_settings': '',
        'moc_id_term': '',
        'moc_term': '',
        'num_filters': '',
        'total_jobs_count': '',
        'results_heading': '',
        'search_url': '',
        'site_commitments': '',
        'site_commitments_string': '',
        'site_config': '',
        'site_description': '',
        'site_heading': '',
        'site_tags': '',
        'site_title': '',
        'title_term': '',
        'view_source': '',
        'widgets': '',
    }


def success_url(request):
    # We specify a nexturl for pages that require login and pages that should
    # redirect back to themselves.
    if request.REQUEST.get('next'):
        return request.REQUEST.get('next')

    # So if we didn't specify the url, redirect to the homepage.
    return reverse('home')
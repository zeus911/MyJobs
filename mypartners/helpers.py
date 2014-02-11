from django.shortcuts import get_object_or_404
from django.http import Http404
from urlparse import urlparse, parse_qsl, urlunparse
from urllib import urlencode

from mydashboard.models import Company


def prm_worthy(request):
    """
    Makes sure the User is worthy enough to use PRM.

    """
    company_id = request.REQUEST.get('company')
    company = get_object_or_404(Company, id=company_id)

    user = request.user
    if not user in company.admins.all():
        raise Http404

    partner_id = int(request.REQUEST.get('partner'))
    partner = get_object_or_404(company.partner_set, id=partner_id)

    return company, partner, user


def url_extra_params(url, feed, extra_urls):
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    query = dict(parse_qsl(query, keep_blank_values=True))
    new_queries = dict(parse_qsl(extra_urls, keep_blank_values=True))
    query.update(new_queries)
    http_url = urlunparse((scheme, netloc, path, params, urlencode(query),
                           fragment))

    (rss_scheme, rss_netloc, rss_path, rss_params, rss_query,
     rss_fragment) = urlparse(feed)
    feed = urlunparse((rss_scheme, rss_netloc, rss_path, rss_params, urlencode(query),
                       rss_fragment))

    return http_url, feed
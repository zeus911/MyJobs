
from datetime import datetime, timedelta
from django.http import Http404
from urlparse import urlparse

from mydashboard.models import Microsite
from solr.helpers import format_date, Solr


def saved_searches(employer, company, candidate):
    """
    Function that gets employer's companies and those companies microsites.
    Will pull the domain out of the employer_microsites. Gathers the
    candidate's saved search urls and then will pull those urls
    out. Lastly, check to see if employer domains match up with
    candidate domains and return a list of urls.

    inputs:
    :employer:	The employer that is looking at candidate's page
    :candidate:	The job seeker that shows up in employer's activitiy feed

    outputs:
                A list of candidate urls.
    """
    if employer in company.admins.all():
        employer_company = company
    else:
        raise Http404
    employer_microsites = Microsite.objects.filter(
        company=employer_company).values_list('url', flat=True)
    employer_domains = [urlparse(url).netloc for url in employer_microsites]
    candidate_urls = candidate.savedsearch_set.values_list('url', flat=True)
    return [url for url in candidate_urls
            if urlparse(url).netloc in employer_domains]

def filter_by_microsite(microsites, solr=None):
    """
    Applies basic solr filters based on company/microsite.

    inputs:
    :microsites: the microsites to filter the SavedSearches on
    :solr: an existing Solr instance

    outputs:
    A solr instance filtered by applicable microsites, sorted by the
        date a SavedSearch was created on.

    """

    if not solr:
        solr = Solr()

    urls = " OR ".join([site.url.replace("http://", "") for site in
                        microsites])
    solr = solr.add_filter_query("SavedSearch_url:(*%s*)" % urls)

    solr = solr.add_filter_query('User_opt_in_employers:true')
    solr = solr.sort('SavedSearch_created_on')

    return solr

def filter_by_date(request, solr=None):
    """
    Applies date filtering.

    inputs:
    :request: a request object including fields from the date_range form
        in mydashboard.html
    :solr: an existing Solr instance

    outputs:
    The solr instance, the start and end dates for the search, and the
        number of days the search covers

    """
    if not solr:
        solr = Solr()

    requested_after_date = request.REQUEST.get('after', False)
    requested_before_date = request.REQUEST.get('before', False)

    date_end = datetime.now()
    # Set date range based on buttons
    if 'today' in request.REQUEST:
        solr = solr.filter_by_time_period('SavedSearch_created_on',
                                          total_days=1)
        date_start = date_end - timedelta(days=1)
    elif 'seven_days' in request.REQUEST:
        solr = solr.filter_by_time_period('SavedSearch_created_on',
                                          total_days=7)
        date_start = date_end - timedelta(days=7)
    elif 'thirty_days' in request.REQUEST:
        solr = solr.filter_by_time_period('SavedSearch_created_on',
                                          total_days=30)
        date_start = date_end - timedelta(days=30)
    # Set date range based on date selection fields.
    else:
        if requested_after_date:
            date_start = datetime.strptime(requested_after_date, '%m/%d/%Y')
        else:
            date_start = request.REQUEST.get('after')
            if date_start:
                date_start = datetime.strptime(date_start, '%m/%d/%Y')
            else:
                # Default range is 30 days.
                date_start = datetime.now() - timedelta(days=30)

        if requested_before_date:
            date_end = datetime.strptime(requested_before_date, '%m/%d/%Y')
        else:
            date_end = request.REQUEST.get('before')
            if date_end:
                date_end = datetime.strptime(date_end, '%m/%d/%Y')
            else:
                # Default start date is today.
                date_end = datetime.now()
        solr = solr.filter_by_date_range(field='SavedSearch_created_on',
                                         date_start=format_date(date_start),
                                         date_end=format_date(date_end))

    date_delta = (date_end - date_start).days

    return solr, date_start, date_end, date_delta
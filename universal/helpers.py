import re
import urllib

from django.shortcuts import get_object_or_404, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from mydashboard.models import Company


def build_url(reverse_url, params):
    return '%s?%s' % (reverse_url, urllib.urlencode(params))


def get_int_or_none(string):
    try:
        return int(string)
    except (ValueError, TypeError, UnicodeEncodeError):
        return None


def get_domain(url):
    """
    Attempts to determine the domain from a url with unknown formatting.

    Created because urlparse.urlparse doesn't handle urls with a
    missing protocol very well. Unfortunately this doesn't handle
    anything except no protocol, http, or https at all.

    """
    pattern = '(http://|https://)?([^/]*\.)?(?P<domain>[^/]*\.[^/]*)'
    pattern = re.compile(pattern)
    try:
        return pattern.search(url).groupdict()['domain'].split("/")[0]
    except (AttributeError, KeyError, TypeError):
        return None


def sequence_to_dict(from_):
    """
    Turns a sequence of repeated key, value elements into a dict. The input
    sequence will be truncated at the last odd index.

    This was originally intended to be used to turn faceted fields returned by
    Solr into a dictionary. These lists are of the form
    ['field_name', facet_count]

    Examples:
    list_to_dict([]) => {}
    list_to_dict(['key_1', 1]) => {'key_1': 1}
    list_to_dict(['key_1', 'value_1', 'key_2']) => {'key_1', 'value_1'}

    Inputs:
    :from_: Sequence to be converted

    Output:
        Dictionary created from the input sequence
    """
    return dict(zip(*[iter(from_)]*2))


def get_company(request):
    """
    Uses the myjobs_company cookie to determine what the current company is.

    """
    if not request.user or request.user.is_anonymous():
        return None
    company = request.COOKIES.get('myjobs_company')
    if company:
        company = get_object_or_404(Company, pk=company)

        # If the company cookie is correctly set, confirm that the user
        # actually has access to that company.
        if company not in request.user.get_companies():
            company = None

    if not company:
        try:
            # If the company cookie isn't set, then the user should have
            # only one company, so use that one.
            company = request.user.get_companies()[0]
        except IndexError:
            company = None
    return company


def get_company_or_404(request):
    """ Simple wrapper around get_company that raises Http404 if no valid 
        company is found.
    """
    company = get_company(request)

    if not company:
        raise Http404
    else:
        return company


def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except (model.DoesNotExist, ValueError):
        return None


def add_pagination(request, object_list):
    """
    Basic Django Pagination -- Pass a list of objects you wish to paginate.
    That listing will be wrapped by the Paginator object then the listing will
    get split into Pages deemed by :objects_per_page:, which is defaulted
    to 10.

    Inputs:
    :object_list:   A list (or Queryset) of an object you wish to paginate.

    Outputs:
        Returns a Paginator Object. Paginator acts as a wrapper for the object
        list you pass through. The objects and their attributes are still
        accessed the same but has added methods for the paginator and the
        pages that are created.

    """
    try:
        objects_per_page = int(request.GET.get('per_page') or 10)
    except ValueError:
        objects_per_page = 10
    page = request.GET.get('page')
    paginator = Paginator(object_list, objects_per_page)

    try:
        pagination = paginator.page(page)
    except PageNotAnInteger:
        pagination = paginator.page(1)
    except EmptyPage:
        pagination = paginator.page(paginator.num_pages)

    return pagination

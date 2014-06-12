from functools import wraps
import urllib

from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect

from universal.helpers import get_company


def company_has_access(perm_field):
    """
    Determines whether or not a user and their current company has access to
    the requested feature.

    inputs:
        :perm_field: The name of the BooleanField on Company that handles
            permissions for the requested feature.

    """
    def decorator(view_func):
        def wrap(request, *args, **kwargs):

            # If the user is not logged in, redirect them to the login page
            # with this url as the next url.
            if request.user.is_anonymous():
                params = {'next': request.path, }
                next_url = build_url(reverse('home'), params)
                return HttpResponseRedirect(next_url)

            # If the user is logged in, but they aren't a CompanyUser or they
            # are a CompanyUser, but their current Company doesn't have
            # perm_field access, return a 404.
            company = get_company(request)
            if not company or not getattr(company, perm_field, False):
                raise Http404

            return view_func(request, *args, **kwargs)
        return wraps(view_func)(wrap)
    return decorator


def build_url(reverse_url, params):
    return '%s?%s' % (reverse_url, urllib.urlencode(params))
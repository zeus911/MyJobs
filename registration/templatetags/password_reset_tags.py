from django.template import Library
from django.conf import settings

from seo.models import SeoSite

register = Library()


@register.simple_tag
def get_current_seosite(attr=None, str_func=None):
    """
    Gets the current seo site and optionally returns an attr of that site as a
    string, which may have a str_func run on it. if settings.SITE is not an
    SeoSite object, the one for secure.my.jobs is returned instead.

    inputs:
    :attr: The SeoSite attribute we are interested in.
    :str_func: the string method to call on the object.

    Example:
    # return the capitalized domain for a site
    >>> {% get_current_seosite 'domain' 'capitalize' %}
    'My.jobs' 
    """

    seosite = getattr(settings, 'SITE') or SeoSite.objects.get(
        domain="secure.my.jobs")

    if attr:
        # the attribute may not always be a string, so we convert it to one
        obj = unicode(getattr(seosite, attr))
        if str_func:
            return getattr(obj, str_func)()

        return obj
    else:
        return seosite

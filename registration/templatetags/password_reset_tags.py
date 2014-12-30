from django.template import Library
from django.conf import settings

register = Library()


@register.simple_tag(takes_context=True)
def get_current_seosite_domain():
    """
    Gets the domain of the current SeoSite.

    """
    domain = 'my.jobs'
    if getattr(settings, 'SITE', None):
        domain = settings.SITE.domain

    return domain.capitalize()

from django import template
from django.core.urlresolvers import reverse

from registration.models import ActivationProfile

register = template.Library()


@register.filter(name='make_verbose_frequency')
def make_verbose_frequency(value):
    if value == 'D':
        return 'Daily'
    if value == 'W':
        return 'Weekly'
    if value == 'M':
        return 'Monthly'


@register.filter(name='time_created')
def time_created(savedsearch):
    return savedsearch.created_on.strftime('%A, %B %d, %Y %l:%M %p')


@register.assignment_tag
def has_attr(obj, attr):
    return hasattr(obj, attr)


@register.assignment_tag
def get_all_jobs_link(saved_search):
    """
    Determines whether saved_search.feed or saved_search.url should be used
    as the view all jobs link.
    """
    url = saved_search.url

    if url.startswith('http://my.jobs'):
        feed = saved_search.feed
        if feed:
            return feed.replace('/feed/rss', '')

    return url


@register.simple_tag
def get_created_url(saved_search):
    """
    Constructs the url for the "yes, I created this" button

    If a user is not active, the link will point to their activation page
    If a user is active, the link will point to the My.jobs saved search
        feed viewer
    """
    user = saved_search.user

    if user.is_active:
        url = reverse('view_full_feed') + '?id={id}&verify={guid}'.format(
            id=saved_search.pk, guid=user.user_guid)
    else:
        url = get_activation_link(user)
    return url


@register.simple_tag
def get_activation_link(user):
    profile, _ = ActivationProfile.objects.get_or_create(user=user,
                                                         email=user.email)
    if profile.activation_key_expired():
        profile.reset_activation()
    url = reverse('registration_activate',
                  args=[profile.activation_key]) + '?verify={guid}'.format(
                      guid=user.user_guid)
    return url

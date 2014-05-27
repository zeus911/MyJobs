from django import template

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
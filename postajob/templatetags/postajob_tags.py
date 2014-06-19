import bleach

from django.core.urlresolvers import resolve
from django.template import Library
from django.utils.text import slugify
from django.utils.safestring import mark_safe


register = Library()


@register.simple_tag
def get_job_links(job):
    sites = job.on_sites()
    domains = [site.domain for site in sites]

    location = u'{city}, {state}'.format(city=job.city, state=job.state_short)
    loc_slug = bleach.clean(slugify(location))
    title_slug = bleach.clean(slugify(job.title))

    base_url = 'http://{domain}/{loc_slug}/{title_slug}/{guid}/job/'
    href_tag = '<a href="{url}">{domain}</a>'
    urls = []
    for domain in domains:
        job_url = base_url.format(domain=domain, loc_slug=loc_slug,
                                  title_slug=title_slug, guid=job.guid)

        urls.append(href_tag.format(url=job_url, domain=domain))
    url_html = mark_safe("<br/>".join(urls[:3]))
    if len(urls) > 3:
        url_html = mark_safe("%s <br/>..." % url_html)
    return url_html


@register.simple_tag(takes_context=True)
def get_form_action(context):
    current_url_name = resolve(context['request'].path).url_name
    if context.get('item') and context['item'].pk:
        return 'Edit'
    elif current_url_name == 'purchasedproduct_add':
        return 'Purchase'
    return 'Add'
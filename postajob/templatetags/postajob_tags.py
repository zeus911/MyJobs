import bleach

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
    return mark_safe("<br/>".join(urls))

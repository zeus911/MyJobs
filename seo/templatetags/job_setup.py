from seo.helpers import featured_default_jobs

from django import template


register = template.Library()

@register.inclusion_tag('job_result.html', takes_context=True)
def arrange_jobs(context):
    featured_jobs = context.get('featured_jobs')
    default_jobs = context.get('default_jobs')
    config = context.get('site_config')
    show_co_names = config.browse_company_show
    request = context.get('request')
    arranged_jobs = create_arranged_jobs(request, featured_jobs, default_jobs,
                                         config)

    query_string = request.META.get('QUERY_STRING', '')
    return {
        'arranged_jobs': arranged_jobs,
        'show_co_names': show_co_names,
        'title_term': context.get('title_term'),
        'query_string': query_string,
        'site_tags': context.get('site_tags')
    }


def create_arranged_jobs(request, featured_jobs, default_jobs, site_config):
    percent_featured = site_config.percent_featured
    jobs_shown = (int(request.GET.get('num_items',
                                      site_config.num_job_items_to_show))
                  if request.is_ajax() else site_config.num_job_items_to_show)

    (f_shown, d_shown, _, _) = featured_default_jobs(len(featured_jobs),
                                                     len(default_jobs),
                                                     jobs_shown,
                                                     percent_featured)
    jobs = []
    if not request.is_ajax():
        # Shown jobs
        jobs.append({
            'jobs': featured_jobs[:f_shown],
            'class': 'featured_jobListing'
        })
        jobs.append({
            'jobs': default_jobs[:d_shown],
            'class': 'default_jobListing'
        })

        # Hidden jobs
        jobs.append({
            'jobs': featured_jobs[f_shown:],
            'class': 'featured_jobListing direct_hiddenOption'
        })
        jobs.append({
            'jobs': default_jobs[d_shown:],
            'class': 'default_jobListing direct_hiddenOption'
        })
    else:
        jobs.append({
            'jobs': featured_jobs,
            'class': 'featured_jobListing direct_hiddenOption'
        })
        jobs.append({
            'jobs': default_jobs,
            'class': 'default_jobListing direct_hiddenOption'
        })

    if not jobs or jobs[0]['jobs'] or not jobs[1]['jobs']:
        jobs = []

    return jobs
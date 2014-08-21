from seo.helpers import featured_default_jobs

from django import template


register = template.Library()

@register.inclusion_tag('job_result.html', takes_context=True)
def arrange_jobs(context):
    featured_jobs = context.get('featured_jobs')
    default_jobs = context.get('default_jobs')
    config = context.get('site_config')
    show_co_names = config.browse_company_show
    percent_featured = config.percent_featured
    request = context.get('request')
    jobs_shown = int(request.GET.get('num_items',
                                     config.num_job_items_to_show)) \
        if request.is_ajax() else config.num_job_items_to_show

    arranged_jobs = []

    (f_shown, d_shown, _, _) = featured_default_jobs(len(featured_jobs),
                                                     len(default_jobs),
                                                     jobs_shown,
                                                     percent_featured)

    if not request.is_ajax():
        # Shown jobs
        arranged_jobs.append({'jobs': featured_jobs[:f_shown], 
                              'class': 'featured_jobListing'})
        arranged_jobs.append({'jobs': default_jobs[:d_shown],
                              'class': 'default_jobListing'})
        
        # Hidden jobs
        arranged_jobs.append({'jobs': featured_jobs[f_shown:], 
                              'class': 'featured_jobListing direct_hiddenOption'})
        arranged_jobs.append({'jobs': default_jobs[d_shown:], 
                              'class': 'default_jobListing direct_hiddenOption'})
    else:
        arranged_jobs.append({'jobs': featured_jobs, 
                              'class': 'featured_jobListing direct_hiddenOption'})
        arranged_jobs.append({'jobs': default_jobs,
                              'class': 'default_jobListing direct_hiddenOption'})
    request = context.get('request', None)
    query_string = request.META.get('QUERY_STRING', '')
    return {'arranged_jobs': arranged_jobs if arranged_jobs[0]['jobs'] \
                             or arranged_jobs[1]['jobs'] else [],
            'show_co_names': show_co_names,
            'title_term': context.get('title_term'),
            'query_string': query_string,
            'site_tags': context.get('site_tags')}

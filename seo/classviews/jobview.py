import re

from django.conf import settings
from seo.classviews.baseview import BaseView


def job_listing(request):
    ## parse the url for other slug values
    slug_tag_value_dict = _parse_slug_tags(request.path)
    
    filters_dict = _map_slugs_to_filters(slug_tag_value_dict)
    
     
def _map_slugs_to_filters(slugs_dict):
    """
    Maps values from slugs_dict to keys from settings.SLUG_TAGS
    
    Example:
     slugs_dict:
        {
            'jobs-in': 'project-manager',
            'jobs': 'usa'
        }
     settings.SLUG_TAGS:
         {'title_slug': '/jobs-in/',
          'location_slug': '/jobs/',
          'facet_slug': '/new-jobs/',
          'moc_slug': '/veteran-jobs/'}
             
     Result:
         {'title_slug': 'project-manager',
          'location_slug': 'usa',
          'facet_slug': None,
          'moc_slug': None}
    
    """
    return dict([(key, slugs_dict.get(value.strip('/'))) for key, value in
                 settings.SLUG_TAGS.items()])
    
    
def _parse_slug_tags(slug_path):
    """
    Parses out the slug tags and associated values into key/value pairs.
    Slug tags are the keys, and values are values.
    
    General Format:
    {value_1}/{slug_tag_1}/{value_2}/{slug_tag_2}/.../{value_n}/{slug_tag_n}/
        
    Example:
        slug_path = "project-manager/jobs-in/usa/jobs/"
        
        returns <Dict>:
        {
            'jobs-in': 'project-manager',
            'jobs': 'usa'
        }
        
        Location values can span across multiple '/':
            boston/ma/usa/jobs
            slug_tag = jobs
            value = boston/ma/usa
    
    """
    slug_value_list = re.findall('([/\w-]+?)/(jobs|jobs-in|new-jobs)/',
                                 slug_path)
    return dict([(key, value) for (value, key) in slug_value_list])



class BaseJobView(BaseView):
    # common Job functionality goes here
    pass

class JobDetailView(BaseJobView):
    template = "job_detail.html"
    
    def __init__(self, request, *args, **kwargs):
        self.request = request
    
    def create_response(self):
        # implementation goes here
        # must return an HTTPResponse out of this method
        # return render_to_response(tmeplate_name, request, context)
        pass
    
job_detail_view = JobDetailView()

class JobListingBySlugTag(BaseJobView):
    template = "job_listing.html"
    
    def __init__(self, request, *args, **kwargs):
        self.request = request
        
    def create_response(self):
        pass
    
job_listing_by_slug_tag = JobListingBySlugTag()
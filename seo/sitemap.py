import datetime
import math
from slugify import slugify
from solrsitemap import SolrSitemap

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import NoReverseMatch, reverse

from seo.search_backend import DESearchQuerySet
from seo.helpers import sqs_apply_custom_facets


class DESolrSitemap(SolrSitemap):
    """ 
    Parse the jobs for a particular domain and return a sitemap. This
    generates a sitemap-pages.xml file for all microsites that contains
    all the URLS on the site, its frequency of update, and when it was
    last modified, for web crawlers to use for indexing.

    This sitemap is "lazy" compared to Django's built-in Sitemap, in that
    it does not fetch the data needed to compute all the URLs at once.
    Instead of using Django's built-in pagination, we delegate pagination
    operations to Solr itself using its `start` and `rows` parameters.
    
    """
    #Required solr document fields. date_new is used by lastmod()
    required_fields = ['date_new']

    def __init__(self, fields=None, queryclass=DESearchQuerySet, **kwargs):
        # 'fields' is an iterable of field names that correspond to fields in
        # the index. Whatever fields you would put into the 'fl' parameter for
        # Solr's API are the same fields that should be present in the 'fields'
        # kwarg.
        self.limit = 2000
        self.fields = fields or []
        self.fields.extend(self.required_fields)
        self.buids = settings.SITE_BUIDS
        self.buid_str = " OR ".join([str(i) for i in self.buids])
        super(DESolrSitemap, self).__init__(queryclass=queryclass, **kwargs)
        
    def _sqs(self):
        sqs = super(DESolrSitemap, self)._sqs()._clone()

        if self.buids:
            sqs = sqs.narrow("buid:(%s)" % self.buid_str)

        sqs = sqs_apply_custom_facets(settings.DEFAULT_FACET, sqs)

        if self.fields:
            sqs = sqs.fields(self.fields)
            
        return sqs
    
    def changefreq(self, obj): 
        """How frequently the sitemap is likely to change"""
        return "monthly" 

    def lastmod(self, obj): 
        #Creates a datetime object from date_new
        return datetime.datetime.strptime(obj.get('date_new'), "%Y-%m-%d-%H%M%S")
    
    def priority(self, obj):
        if obj['type'] == 'job_detail':
            return 1.0

    def location(self, obj):
        # Mapping of URL types to the data associated with each type. This
        # allows us to build out the arguments to our ``reverse`` call
        # while avoiding writing (and more importantly, maintaining) a bunch of
        # boilerplate.
        paths = {
            'location': {
                'name': 'location',
                'kwargs': ['location']
            },
            'title_location': {
                'name': 'title_location',
                'kwargs': ['location', 'title']
            },
            'job_detail': {
                'name': 'job_detail_by_location_slug_title_slug_job_id',
                'kwargs': ['location', 'title', 'uid']
            }
        }
        # Mapping of ``obj`` keys to keyword arguments that must be passed to
        # the view specified. As with the ``paths`` dictionary, this is being
        # used to eliminate repetitive code that is difficult to maintain.
        fields = {
            'location': 'location_slug',
            'title': 'title_slug',
            'uid': 'job_id'
        }
        info = paths[obj['type']]
        kwargs = dict((fields[i], obj[i]) for i in info['kwargs'])
        return reverse(info['name'], kwargs=kwargs)

    def get_urls(self, site=None):
        if site is None:
            if Site._meta.installed:
                try:
                    site = Site.objects.get_current()
                except Site.DoesNotExist:
                    pass
            if site is None:
                raise ImproperlyConfigured("""In order to use Sitemaps you must\
                                            either use the sites framework or\
                                            pass in a Site or RequestSite\
                                            object in your view code.""")

        urls = []
        sitemap_view_source = settings.FEED_VIEW_SOURCES.get('sitemap', 28)
        for item in self.items():
            # If there's some data in the job feed that is not recognized by
            # our url patterns, it will cause `reverse()` to throw a
            # `NoReverseMatch` exception. If we don't catch that here, it will
            # cause the entire sitemap page to return a 500. We want to just
            # exclude the link to that job.
            try:
                loc = "http://%s/%s%d" % (site.domain, item['guid'],
                                          sitemap_view_source)
            except NoReverseMatch:
                continue
            else:
                priority = self.priority(item)
                url_info = {
                    'location':   loc,
                    'lastmod':    self.lastmod(item),
                    'changefreq': self.changefreq(item),
                    'priority':   str(priority is not None and priority or '')
                }
                urls.append(url_info)
        return urls

    def items(self):
        """
        Return a list of dictionaries needed to create the URLs.
        In format field:value
        
        """
        end = int(self.pagenum) * self.limit
        start = end - self.limit
        results = self.results.values(*self.fields)[start:end]
        items = []
        
        for d in results:
            # If there are any values in the dictionary that, when slugified,
            # yield empty strings, continue without evaluating further.
            if not all([slugify(v) for v in d.values()]):
                continue
                
            ret = dict((k, slugify(v)) for k, v in d.items())
            ret['type'] = 'job_detail'
            items.append(ret)

        return items


class DateSitemap(DESolrSitemap):
    """
    Works just like DESolrSitemap, except it also filters jobs by a
    particular date, passed to the constructor as a `datetime.datetime`
    object.
    
    """    
    def __init__(self, jobdate=None, **kwargs):
        """
        Inputs:
        :jobdate: datetime.date object.
        
        """
        if not jobdate:
            jobdate = datetime.date.today()
        else:
            jobdate = datetime.datetime.strptime(jobdate, "%Y-%m-%d").date()

        self.jobdate = jobdate.timetuple()
        super(DateSitemap, self).__init__(**kwargs)
        self.results = self._sqs()._clone()

    def _sqs(self):
        """
        Filters the search results returned from DESolrSitemap to only
        include jobs from `self.jobdate`.
        
        """
        sqs = super(DateSitemap, self)._sqs()._clone()
        return sqs.filter(date_new__range=self._daterange())

    def numpages(self, startdate, enddate, field='date_new'):
        """
        This method gets the counts for each individual date in the
        `[startdate, enddate]` date range. By default, the `numpages`
        method makes an HTTP request to Solr for every date.

        This method will not work if the DateSitemap instance it is bound
        to is passed a value for `fields` during instantiation. This is
        because if it is passed a value for `fields`, the return value of
        the `_sqs` method will be of type ValuesSearchQuerySet, which
        does not have a `facet_limit` method.
        Inputs::
        :startdate: 
        :enddate:
        
        """
        # The date format Solr uses to represent dates.
        solr_date_fmt = "%Y-%m-%dT%H:%M:%SZ"
        # We want as little data returned as possible, so we'll specify that
        # we only want Solr to return the 'uid' field (along with a handful
        # of fields that Haystack requires, but those are added behind the
        # scenes in seo.search_backend.DESolrQuery).
        sqs = super(DateSitemap, self)._sqs()._clone().fields(['uid'])
        # In Haystack, the idiomatic way to get specify some number of rows
        # aside from the default number (10, usually) is to use slice notation,
        # so like sqs[0:20] to get 20 rows. However this won't work for us since
        # we're just after the facets, and once you take a slice, you can't
        # further modify the SearchQuerySet. So instead we'll specify what rows
        # we want "manually" here by setting these two attributes.
        sqs.query.start_offset = 0
        sqs.query.end_offset = 1
        # A facet.limit of -1 means no limit to the number of facets that will
        # be returned. If we don't set this setting, it will only return the
        # default number of facets (10, by default).
        sqs = sqs.filter(date_new__range=[startdate, enddate])\
                 .date_facet(field, startdate, enddate, gap_by='day')\
                 .facet_limit(-1)
        facetcounts = dict(sqs.facet_counts()['dates'][field])

        # Haystack puts some 'administrative' data in with the facet counts, so
        # let's remove those before proceeding.
        for k in ['start', 'end', 'gap']:
            del facetcounts[k]
            
        for k, v in facetcounts.items():
            # Convert date string to a datetime object.
            try:
                dt = datetime.datetime.strptime(k, solr_date_fmt)
            except ValueError:
                # The date facet returns an oddball date that I do not
                # understand; for now, we'll just remove it from 'facetcounts'
                # and continue through the loop. Could stand to be re-examined
                # to sort out what that date is and why it is in the results.
                del facetcounts[k]
                continue
                
            # Only get year, month and day values.
            ymd = datetime.date(*dt.timetuple()[0:3]).isoformat()
            # Divide the number of results by self.limit and round up to derive
            # the number of pages required to display all the jobs for a given
            # date. When we add it to the dictionary, however, coerce it to an
            # int. Using a float with range is deprecated.
            val = math.ceil(float(facetcounts.pop(k))/self.limit)
            facetcounts[ymd] = int(val)

        return facetcounts

    def _daterange(self, date_val=None):
        if date_val is None:
            date_val = self.jobdate

        oneday = datetime.timedelta(hours=23, minutes=59, seconds=59)
        lastnight = datetime.datetime(*date_val[0:3])
        tonight = lastnight + oneday
        return [lastnight, tonight]

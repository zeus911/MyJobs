from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import QueryDict
from django.template.loader import render_to_string

from seo import helpers
from seo.models import CustomFacet


class Breadbox(object):
    class Breadcrumb(object):
        def __init__(self, url, display_title,
                     breadcrumb_class='breadcrumb_bread_box'):
            self.url = url
            self.display_title = display_title
            self.breadcrumb_class = breadcrumb_class

    def __init__(self, path, filters, jobs, query_dict):
        self.path = path
        self.filters = filters
        self.jobs = jobs
        self.query_dict = query_dict

        # Set defaults for the breadcrumb types so that the functions that
        # create them aren't responsible for guaranteeing their existance.
        self.company_breadcrumbs = []
        self.custom_facet_breadcrumbs = []
        self.location_breadcrumbs = []
        self.moc_breadcrumbs = []
        self.q_breadcrumbs = []
        self.title_breadcrumbs = []

        self.clear_breadcrumbs = []

        self.build_breadcrumbs()

    def _make_clear_breadcrumb(self):
        if self.clear_breadcrumb is not []:
            self.clear_breadcrumb = [self.Breadcrumb(url=reverse('all_jobs'),
                                                     display_title='Clear All')]

    def _make_url(self, path=None, query_dict=None):
        path = path or self.path
        query_dict = query_dict or self.query_dict
        return "%s?%s" % (path, query_dict.urlencode())

    def _remove_param_from_query_dict(self, param):
        query_dict = QueryDict(self.query_dict).copy()
        if param in query_dict:
            del query_dict[param]
        return query_dict

    def build_breadcrumbs(self):
        self.build_param_breadcrumbs()
        self.build_filter_breadcrumbs()

    def build_breadcrumb_for_slug_type(self, slug_type, display_title):
        ending_slug = settings.SLUG_TAGS[slug_type]
        breadcrumb_class = slug_type.replace('_slug', '_bread_box')

        if self.filters.get(slug_type):
            slug = self.filters[slug_type].strip('/')
            path_for_slug = "%s/%s" % (slug, ending_slug)
            new_path = self.path.replace(path_for_slug, '')
            kwargs = {
                'breadcrumb_class': breadcrumb_class,
                'display_title': display_title,
                'url': self._make_url(path=new_path)
            }
            return self.Breadcrumb(**kwargs)
        return None

    def build_breadcrumb_for_param(self, param):
        param_value = self.query_dict.get(param)
        if param_value:
            updated_query_dict = self._remove_param_from_query_dict(param)
            updated_url = self._make_url(query_dict=updated_query_dict)
            kwargs = {
                'breadcrumb_class': '%s_bread_box' % param,
                'url': updated_url,
                'display_title': param_value,
            }
            return self.Breadcrumb(**kwargs)

    def build_company_breadcrumbs_from_slugs(self):
        company_slug_value = self.filters.get('company_slug')
        display_title = helpers.bread_box_company_heading(company_slug_value)
        breadcrumb = self.build_breadcrumb_for_slug_type('company_slug',
                                                         display_title)
        if breadcrumb:
            self.company_breadcrumbs = [breadcrumb]
            self._make_clear_breadcrumb()

    def build_custom_facet_breadcrumbs_from_slugs(self):
        ending_slug = settings.SLUG_TAGS['facet_slug']
        if self.filters.get('facet_slug'):
            facet_filters = self.filters['facet_slug'].strip('/')
            facet_filters = facet_filters.split('/')
            custom_facets = CustomFacet.objects.prod_facets_for_current_site()
            custom_facets = custom_facets.filter(name_slug__in=facet_filters)

            # If there's at most one path that we can remove, then
            # remove the ending slug as well.
            new_path = self.path
            if custom_facets.count() < 2:
                new_path.replace(ending_slug, '')

            self.custom_facet_breadcrumbs = []
            for facet in custom_facets:
                new_path = new_path.replace(facet.name_slug, '')
                kwargs = {
                    'breadcrumb_class': 'facet_bread_box',
                    'display_title': facet.name,
                    'url': self._make_url(path=new_path)
                }
                self.custom_facet_breadcrumbs.append(self.Breadcrumb(**kwargs))
                self._make_clear_breadcrumb()

    def build_filter_breadcrumbs(self):
        self.build_company_breadcrumbs_from_slugs()
        self.build_custom_facet_breadcrumbs_from_slugs()
        self.build_location_breadcrumbs_from_slugs()
        self.build_moc_breadcrumbs_from_slugs()
        self.build_title_breadcrumbs_from_slugs()

    def build_location_breadcrumbs_from_slugs(self):
        ending_slug = settings.SLUG_TAGS['location_slug']

        if self.filters.get('location_slug'):
            location_slug = self.filters['location_slug'].strip('/')
            display_title = helpers.bread_box_location_heading(location_slug,
                                                               jobs=self.jobs)
            location_filters = location_slug.split('/')
            location_filters = filter(lambda x: x != 'none', location_filters)

            new_path = self.path

            # If there's only a country then we can safely remove the
            # ending slug as well.
            if len(location_filters) < 2:
                new_path = new_path.replace(ending_slug, '')

            new_location_slug = "/".join(location_filters[1:])
            new_path = new_path.replace(location_slug, new_location_slug)

            kwargs = {
                'breadcrumb_class': 'location_bread_box',
                'display_title': display_title,
                'url': self._make_url(path=new_path)
            }
            self.location_breadcrumbs = [self.Breadcrumb(**kwargs)]
            self._make_clear_breadcrumb()

    def build_location_breadcrumbs_from_params(self):
        location = self.build_breadcrumb_for_param('location')
        if location:
            self.location_breadcrumbs = [location]
            self._make_clear_breadcrumb()

    def build_moc_breadcrumbs_from_params(self):
        moc = self.build_breadcrumb_for_param('moc')
        if moc:
            self.moc_breadcrumbs = [moc]
            self._make_clear_breadcrumb()

    def build_moc_breadcrumbs_from_slugs(self):
        moc_slug_value = self.filters.get('moc_slug')
        display_title = helpers.bread_box_moc_heading(moc_slug_value)

        breadcrumb = self.build_breadcrumb_for_slug_type('moc_slug',
                                                         display_title)
        if breadcrumb:
            self.moc_breadcrumbs = [breadcrumb]
            self._make_clear_breadcrumb()

    def build_param_breadcrumbs(self):
        self.build_location_breadcrumbs_from_params()
        self.build_moc_breadcrumbs_from_params()
        self.build_q_breadcrumbs_from_params()

    def build_q_breadcrumbs_from_params(self):
        q = self.build_breadcrumb_for_param('q')
        if q:
            self.q_breadcrumbs = [q]
            self._make_clear_breadcrumb()

    def build_title_breadcrumbs_from_slugs(self):
        title_slug_value = self.filters.get('title_slug')
        display_title = helpers.bread_box_title_heading(title_slug_value,
                                                        jobs=self.jobs)
        breadcrumb = self.build_breadcrumb_for_slug_type('title_slug',
                                                         display_title)
        if breadcrumb:
            self.title_breadcrumbs = [breadcrumb]
            self._make_clear_breadcrumb()

    def render(self):
        return render_to_string('includes/breadbox.html', {'breadbox': self})
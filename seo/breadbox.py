from django.http import QueryDict


class Breadbox(object):
    class Breadcrumb(object):
        url = None
        display_title = None

        def __init__(self, url=None, display_title=None):
            self.url = url
            self.display_title = display_title

    clear_breadcrumb = Breadcrumb(url='/jobs/', display_title='Clear All')
    company_breadcrumbs = None
    facet_breadcrumbs = None
    location_breadcrumbs = None
    moc_breadcrumbs = None
    q_breadcrumbs = None

    def __init__(self, path, filters, query_dict):
        self.path = path
        self.filters = filters
        self.query_dict = query_dict

    def _make_url(self, path=None, query_dict=None):
        path = path or self.path
        query_dict = query_dict or self.query_dict
        return "%s?%s" % (path, query_dict.urlencode())

    def _remove_param_from_query_dict(self, param):
        query_dict = QueryDict(self.query_dict).copy()
        if param in query_dict:
            del query_dict[param]
        return query_dict

    def build_location_breadcrumbs(self):
        location = self.query_dict.get('location')
        if location:
            updated_query_dict = self._remove_param_from_query_dict('location')
            updated_url = self._make_url(query_dict=updated_query_dict)
            kwargs = {
                'url': updated_url,
                'display_title': location
            }
            self.location_breadcrumbs = [self.Breadcrumb(**kwargs)]

    def build_param_breadcrumbs(self):
        self.build_location_breadcrumbs()
        self.build_q_breadcrumbs()

    def build_q_breadcrumbs(self):
        q = self.query_dict.get('q')
        if q:
            updated_query_dict = self._remove_param_from_query_dict('q')
            updated_url = self._make_url(query_dict=updated_query_dict)
            kwargs = {
                'url': updated_url,
                'display_title': q,
            }
            self.q_breadcrumbs = [self.Breadcrumb(**kwargs)]



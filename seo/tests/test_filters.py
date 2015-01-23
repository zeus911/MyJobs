# -*- coding: utf-8 -*-
from re import finditer

from django.core.urlresolvers import reverse_lazy

from seo import helpers
from setup import DirectSEOBase


filter_types = ['city', 'state', 'country', 'title', 'company', 'moc',
                'mapped_moc', 'facet']


class DummyRequest():
    def __init__(self, path=reverse_lazy('view_jobs'), query_string=None):
        self.path = path
        if query_string:
            self.META = {'QUERY_STRING': query_string}


class DummyConfig():
    def __init__(self):
        self.num_filter_items_to_show = 5
        #Add browse_foo_text for each _type you pass to Widget
        i = 0
        for filter_type in filter_types:
            i += 1
            setattr(self, 'browse_%s_show' % filter_type, True)
            setattr(self, 'browse_%s_order' % filter_type, i)
            setattr(self, 'browse_%s_text' % filter_type, filter_type)


class FiltersTestCase(DirectSEOBase):

    def setUp(self):
        super(FiltersTestCase, self).setUp()
        self.request = DummyRequest()
        self.config = DummyConfig()

    def test_no_facets(self):
        """
        Any widget without items shouldn't even attempt to render.

        """
        facet_counts = {}
        for filter_type in filter_types:
            facet_counts['%s_slab' % filter_type] = []
        widgets = helpers.get_widgets(self.request, self.config,
                                      facet_counts, custom_facets=[])
        for widget in widgets:
            self.assertIsNone(widget.render())

    def test_no_more_less(self):
        """
        Any widget without more items to show should not include the
        more/less buttons.

        """
        slab = 'usa/jobs::United States'
        facet_counts = {}
        for filter_type in filter_types:
            items = []
            for i in range(self.config.num_filter_items_to_show-1):
                items.append((slab, 5))
            facet_counts['%s_slab' % filter_type] = items
        widgets = helpers.get_widgets(self.request, self.config, 
                                      facet_counts,
                                      custom_facets=facet_counts['facet_slab'])
        for widget in widgets:
            self.assertEqual(widget.render().find('More'), -1) 
            self.assertEqual(widget.render().find('Less'), -1)

    def test_more_less(self):
        """
        Widgets with more items to show should include the more/less buttons.

        """
        slab = 'usa/jobs::United States'
        facet_counts = {}
        for filter_type in filter_types:
            items = []
            for i in range(self.config.num_filter_items_to_show+1):
                items.append((slab, 5))
            facet_counts['%s_slab' % filter_type] = items
        widgets = helpers.get_widgets(self.request, self.config,
                                      facet_counts,
                                      custom_facets=facet_counts['facet_slab'])
        for widget in widgets:
            self.assertNotEqual(widget.render().find('More'), -1)
            self.assertNotEqual(widget.render().find('Less'), -1)

    def test_widget_state_count(self):
        """
        Regression test, more button was not being shown on state filters
        where international state slabs were not being displayed but were
        assumed to be valid filters by get_widgets.

        """
        # We only need some values from the config
        # Slabs with None in their location name are not rendered by the widgets
        good_bad_slabs = {
            'state': ('california/usa/jobs::California', 
                      'none/irl/jobs::None'),
            'city': ('gary/indiana/usa/jobs::Indiana',
                     'none/indiana/usa/jobs::None'),
            'default': ('foo::foo', 'none::None')}

        for filter_type in filter_types:
            slabs = good_bad_slabs.get(filter_type, good_bad_slabs['default'])
            good_slab = slabs[0]
            bad_slab = slabs[1]
        items = []
        # There are more than 5 valid slabs to display for each type, but they
        # do not occur in the first 10 items o
        good_slab_i = (0, 4, 5, 7, 15, 16, 17, 23, 24, 25)
        for i in range(30):
            if i in good_slab_i:
                items.append((good_slab, i))
            else:
                items.append((bad_slab, i))
        facet_counts = {}
        for filter_type in filter_types:
            facet_counts['%s_slab' % filter_type] = items
        widgets = helpers.get_widgets(self.request, self.config, facet_counts,
                                      custom_facets=facet_counts['facet_slab'])

        # There should be a more button rendered by every widget
        offset = self.config.num_filter_items_to_show * 2
        for widget in widgets:
            self.assertNotEqual(widget.render().find('More'), -1)
            if widget._type != 'facet':
                self.assertIn('data-offset="%s"' % offset, widget.render())
            else:
                # Facet offset should always be larger, since all the facets
                # are loaded at once.
                self.assertNotIn('data-offset="%s"' % offset, widget.render())

    def test_with_existing_path(self):
        """
        For non-custom-facet facets the new path should be stacked on
        top of the current path unless the new path and old path are
        for the same facet type.

        Note: Because the paths stack, custom facets don't follow this
              structure.

        """
        paths_and_included_facet_types = [
            ('/new-york/new-york/usa/jobs/', ['city', 'state', 'country']),

            ('new-york/new-york/usa/jobs/jpmorgan-chase/careers/',
             ['company', 'city', 'state', 'country']),

            ('/retail-store-shift-supervisor/jobs-in/', ['title']),

            ('retail-store-shift-supervisor/jobs-in/indiana/usa/jobs/',
             ['title', 'city', 'state', 'country'])
        ]

        facet_counts = {}

        slab = 'electronics-technician/ET/navy/vet-jobs::Electronics Technician'

        num_items = self.config.num_filter_items_to_show + 1

        for filter_type in filter_types:
            items = []
            for i in range(num_items):
                items.append((slab, 5))
            facet_counts['%s_slab' % filter_type] = items

        custom_facets = facet_counts['facet_slab']
        for path, included_slug_types in paths_and_included_facet_types:
            filters = helpers.build_filter_dict(path)
            request = DummyRequest(path)
            widgets = helpers.get_widgets(request, self.config, facet_counts,
                                          custom_facets=custom_facets,
                                          filters=filters)
            for widget in widgets:
                for filter_type, value in filters.iteritems():
                    # If the path isn't being overwritten, there slug
                    # from the existing path should appear the same
                    # number of times that there are elements in the widget.
                    if value and widget._type not in included_slug_types:
                        matches = list(finditer(value, widget.render()))
                        self.assertEqual(len(matches), num_items)
                    elif value and widget.facet_type_to_slug() == filter_type:
                        matches = list(finditer(value, widget.render()))
                        self.assertEqual(len(matches), 0)
                    elif value:
                        matches = list(finditer(value, widget.render()))
                        self.assertEqual(len(matches), num_items)

    def test_with_custom_facet_existing_path(self):
        """
        For custom facets the new path should be stacked on
        top of the current path.

        """
        facet_counts = {}

        slab = 'taco-truck-driver/new-jobs::Taco Truck Driver'

        num_items = self.config.num_filter_items_to_show + 1

        for filter_type in filter_types:
            items = []
            for i in range(num_items):
                items.append((slab, 5))
            facet_counts['%s_slab' % filter_type] = items

        path = '/mechanic-jobs/new-jobs/'
        filters = helpers.build_filter_dict(path)
        request = DummyRequest(path)
        custom_facets = facet_counts['facet_slab']
        widgets = helpers.get_widgets(request, self.config, facet_counts,
                                      custom_facets=custom_facets,
                                      filters=filters)
        for widget in widgets:
            if widget._type == 'facet':
                new_path = '/mechanic-jobs/taco-truck-driver/new-jobs/'
                matches = list(finditer(new_path, widget.render()))
                self.assertEqual(len(matches), num_items)

    def test_with_existing_query_params(self):
        """
        Query strings should always be stacked on top of new paths.

        """
        facet_counts = {}

        slab = 'electronics-technician/ET/navy/vet-jobs::Electronics Technician'

        num_items = self.config.num_filter_items_to_show + 1

        for filter_type in filter_types:
            items = []
            for i in range(num_items):
                items.append((slab, 5))
            facet_counts['%s_slab' % filter_type] = items
        custom_facets = facet_counts['facet_slab']

        query_string = 'q=taco'
        request = DummyRequest(query_string=query_string)

        widgets = helpers.get_widgets(request, self.config, facet_counts,
                                      custom_facets=custom_facets)
        for widget in widgets:
            matches = list(finditer(query_string, widget.render()))
            self.assertEqual(len(matches), num_items)

        query_string = 'location=Paris, FR'
        request = DummyRequest(query_string=query_string)

        widgets = helpers.get_widgets(request, self.config, facet_counts,
                                      custom_facets=custom_facets)
        for widget in widgets:
            matches = list(finditer(query_string, widget.render()))
            self.assertEqual(len(matches), num_items)




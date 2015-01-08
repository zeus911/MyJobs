# -*- coding: utf-8 -*-
from seo import helpers
from setup import DirectSEOBase


filter_types = ['city', 'state', 'country', 'title', 'company', 'moc',
                'mapped_moc']


class DummyRequest():
    def __init__(self):
        self.path = '/jobs/'


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

    def test_no_more_less(self):
        slab = 'usa/jobs::United States'
        facet_counts = {}
        for filter_type in filter_types:
            items = []
            for i in range(self.config.num_filter_items_to_show-1):
                items.append((slab, 5))
            facet_counts['%s_slab' % filter_type] = items
        widgets = helpers.get_widgets(self.request, self.config, 
                                      facet_counts, custom_facets=[])
        for widget in widgets:
            self.assertEqual(widget.render().find('More'), -1) 
            self.assertEqual(widget.render().find('Less'), -1) 

    def test_widget_state_count(self):
        """
        Regression test, more button was not being shown on state filters
        where international state slabs were not being displayed but were
        assumed to be valid filters by get_widgets
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

        path_dict = helpers.get_bread_box_path()
        widgets = helpers.get_widgets(self.request, self.config, facet_counts, 
                                      custom_facets=[], path_dict=path_dict)

        # There should be a more button rendered by every widget
        for widget in widgets:
            self.assertNotEqual(widget.render().find('More'), -1)

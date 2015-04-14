# -*- coding: utf-8 -*-
from api.helpers import get_query
from api.tests.setup import BaseTestCase


class Helpers(BaseTestCase):
    def test_bad_tm(self):
        query_dict = {'tm': 'oranges', }
        solr_search = get_query(query_dict, self.user)
        self.assertEqual(solr_search.solr_parameters['fq'], [])

        query_dict = {'tm': '3.5', }
        solr_search = get_query(query_dict, self.user)
        self.assertEqual(solr_search.solr_parameters['fq'], [])

    def test_special_chars(self):
        query_dict = {'kw': u'diseño', }
        get_query(query_dict, self.user)

        query_dict = {'kw': u'ччгдхз', }
        get_query(query_dict, self.user)

    def test_boolean_location(self):
        query_dict = {
            'rd1': '0',
            'zc1': 'OR',
        }
        solr_search = get_query(query_dict, self.user)
        self.assertIsNone(solr_search.error)

        query_dict = {
            'rd1': '0',
            'zc1': 'Portland, OR',
        }
        solr_search = get_query(query_dict, self.user)
        self.assertIsNone(solr_search.error)
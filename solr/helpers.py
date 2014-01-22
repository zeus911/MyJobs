import pysolr

from datetime import datetime, timedelta
from django.conf import settings


class Solr(object):
    def __init__(self, solr_location=settings.SOLR_LOCATION):
        self.solr = pysolr.Solr(solr_location)
        self.q = '*:*'
        self.params = {
            'fq': [],
            'fl': [],
            'start': 0,
            'rows': 10,
            'sort': '',
            'wt': 'json',
            'facet': 'false',
            'facet.field': [],
            'facet.query': [],
        }

    def _clone(self):
        clone = Solr()
        clone.q = self.q
        clone.params = self.params
        return clone

    def add_query(self, query_string, bool_operator='AND'):
        """
        Adds the query_string to the query. If the query already exists, adds
        the new query string to the existing query seperated by bool_operator.

        inputs:
        :query_string: The query string to be added.
        :bool_operator: The operator separating query strings. Only used if
            query strings are added multiple times.

        """
        solr = self._clone()
        if solr.q == '*:*':
            solr.q = "(%s)" % query_string
        else:
            solr.q = "%s %s (%s)" % (solr.q, bool_operator, query_string)
        return solr

    def add_filter_query(self, query_string):
        """
        Adds a filter query.

        inputs:
        :query_string: The filter query to be added.

        """
        solr = self._clone()
        solr.params['fq'].append(query_string)
        return solr

    def add_return_field(self, field, alias=None):
        """
        Adds a field to be returned with results. Leave blank to return all
        fields.

        inputs:
        :field: The field to be returned with the results. Can be a
            solr-supported function.
        :alias: The name the field name that the requested field is rerturned
            as.

        """
        solr = self._clone()
        if not alias:
            solr.params['fl'].append(field)
        else:
            solr.params['fl'].append("%s:%s" % (alias, field))
        return solr

    def result_start_row(self, start):
        """
        Sets the starting row for result retrieval. Default is 0.

        """
        solr = self._clone()
        solr.params['start'] = start
        return solr

    def result_rows_to_fetch(self, rows):
        """
        Sets the total number of rows to fetch. Default is 10.

        """
        solr = self._clone()
        solr.params['rows'] = rows
        return solr

    def add_facet_field(self, field):
        """
        Adds a field to facet on.

        """
        solr = self._clone()
        solr.params['facet'] = 'true'
        solr.params['facet.field'].append(field)
        return solr

    def add_facet_query(self, query_string):
        """
        Adds a query to facet on.

        """
        solr = self._clone()
        solr.params['facet'] = 'true'
        solr.params['facet.field'].append(query_string)
        return solr

    def sort(self, sort_field, order='desc'):
        solr = self._clone()
        query = '{sort_field} {order}'
        solr.params['sort'] = query.format(sort_field=sort_field, order=order)
        return solr


    def reset(self):
        """
        Resets all of the fields to their defaults.

        """
        solr = self._clone()
        solr.q = '*:*'
        solr.params = {
            'fq': [],
            'start': 0,
            'rows': 10,
            'sort': '',
            'wt': 'json',
            'facet': 'false',
            'facet.field': [],
            'facet.query': [],
        }
        return solr

    def search(self):
        return self.solr.search(q=self.q, **self.params)

    def delete(self):
        """
        Deletes all documents matching the current search.

        """
        self.solr.delete(self.params)

    def filter_by_time_period(self, field, date_end=datetime.now(),
                              total_days=1):
        """
        Adds a filter spanning one or more days, ending on date_end.

        inputs:
        :field: The field that contains the time period being filtered on.
        :date_end: The latest date included in the search.
        :total_days: The total number of days the search should span.

        """
        solr = self._clone()
        query = "{field}:[{date_end}-{total_days}DAYS TO {date_end}]"
        time_filter = query.format(field=field, total_days=total_days,
                                   date_end=format_date(date_end))
        #solr.add_filter_query(time_filter)
        return solr

    def filter_by_date_range(self, field,
                             date_start=datetime.now()-timedelta(days=1),
                             date_end=datetime.now()):
        """
        Adds a filter spanning one or more days, ending on date_end.

        inputs:
        :field: The field that contains the date range being filtered on.
        :date_end: The latest date included in the search.
        :total_days: The total number of days the search should span.

        """
        solr = self._clone()
        query = "{field}:[{date_start} TO {date_end}]"
        time_filter = query.format(field=field, date_start=date_start,
                                   date_end=date_end)
        #solr.add_filter_query(time_filter)
        return solr


def format_date(date):
    """
    Switches dates to the solr format, ignoring time zones because the pysolr
    upload does the same.

    inputs:
    :date: The datetime object to be solr formatted.

    outputs:
    A date formated YYYY-mm-ddThh:mm:ssZ, e.g. 2013-08-14T20:03:12Z
    """
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    return date.strftime(date_format)

def dict_to_object(results):
    objs = []
    for x in results:
        objs.append(type('SearchResult', (object, ), x))
    return objs
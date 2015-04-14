import json
from urlparse import parse_qsl

from django.core.management.base import BaseCommand, CommandError

from api.helpers import (add_geolocation, simple_api_fields, api_to_solr,
                         get_object_or_blank_string, param_mapper)
from api.models import APIUser, Country, Industry, Search


class Command(BaseCommand):
    help = "Import SearchIDs from .csv"

    def handle(self, *args, **kwargs):
        csv_file = args[0]
        try:
            csv_file = open(csv_file, 'r')
        except Exception, e:
            raise CommandError(e)

        searches = csv_file.readlines()
        # Expecting columns: SearchID [0], VisitorID [1], SearchDate [2],
        # SearchedFrom [3], InitialSearch [4], CurrentSearch [5],
        # XMLSearch [6], UL [7], UC [8], UK [9], UA [10],
        # ResultsDB [11]
        not_added = []

        search_lines = []

        for line in searches:
            line = line.replace('\\n', '').replace('\n', '')
            line = line.split(',')

            search_id = line[0]
            search = line[3].split(' - ')
            try:
                key = search[0]
                query = search[1]
            except Exception:
                if 'Copied' not in line[3]:
                    not_added.append(line)
            else:
                search_lines.append((search_id, query, key))

        new_ids = [x[0] for x in search_lines]
        Search.objects.filter(pk__in=new_ids).delete()

        searches_to_add = [get_query(x[0], x[1], x[2]) for x in search_lines]

        if searches_to_add:
            from api.import_jobs import grouper
            s = grouper(searches_to_add, 15000)
            for x in s:
                Search.objects.bulk_create(filter(None,searches_to_add))
        print not_added


def get_query(search_id, query, key):
    query_dict = dict(parse_qsl(query))
    api_user = APIUser.objects.get(key=key)
    query_string, error, prev_search = '', '', None

    solr_parameters = {'fq': [],
                       'bf': 'recip(ms(NOW/HOUR,salted_date),1.8e-9,1,1)'}

    if query_dict.get('si'):
        # If it's a search ID then we've already recorded the search.
        return

    for param, value in query_dict.items():
        if param == 'so' and value:
            value = ('%s desc' % api_to_solr['tm'] if value == 'initdate'
                     else 'score desc')
        elif param == 'tm' and value:
            value = "[NOW-%sDAY TO NOW]" % value
        elif param in ['onet', 'onets'] and value:
            param = 'onet'
            value = value.replace(",", " OR ").replace('-', '').replace('.', '')
            value = value.replace('000000', '*')
        elif param == 'cn' and value:
            value = get_object_or_blank_string(Country,
                                               {'country_code': value},
                                               attr='country')
        elif param == 'i' and value:
            if value == 'e':
                value = 'False'
            elif value == 's':
                value = 'True'
            else:
                continue
        elif param == 'ind' and value:
            value = get_object_or_blank_string(Industry, {'industry_id': value},
                                               attr='industry')
            value = '"%s"' % value
        elif param == 're' and value:
            try:
                start = int(query_dict.get('rs', 1))
            except (ValueError, TypeError, UnicodeEncodeError):
                start = 0
            try:
                value = value if int(value) <= start + 499 else start + 499
            except (ValueError, TypeError, UnicodeEncodeError):
                value = start + 10
        if param in simple_api_fields and value:
            solr_parameters['fq'].append('%s:(%s)' % (api_to_solr[param],
                                                      value))
        elif param in param_mapper and value:
            solr_parameters[param_mapper[param]] = value

    req_loc = query_dict.get('zc', None)
    if req_loc:
        query_string, solr_parameters = add_geolocation(req_loc, 25,
                                                        query_string,
                                                        solr_parameters, True)
    else:
        req_loc = query_dict.get('zc1', None)
        radius = query_dict.get('rd1', 25)
        if req_loc:
            query_string, solr_parameters = add_geolocation(req_loc, radius,
                                                            query_string,
                                                            solr_parameters)

    kw_list = query_dict.get('kw', '').replace("!=", "-").replace("|", " OR ") \
        .replace("&", " AND ")
    if kw_list:
        query_string = "%s (%s)" % (query_string, kw_list)

    jvid = query_dict.get('jvid', '')[:32]
    if jvid and api_user.jv_api_access:
        solr_parameters['fq'] = ['(guid:(%s))' % jvid]
        query_string = ''

    if not query_string:
        query_string = "*:*"

    if api_user.scope != '1':
        solr_parameters['fq'].append('(network: (true))')

    params_str = json.dumps(solr_parameters)

    return Search(pk=search_id, query=query_string,
                  solr_params=params_str, user=api_user)






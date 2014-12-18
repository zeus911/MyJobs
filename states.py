import json
import urllib2


def get_state_map():
    data_url = 'https://d2e48ltfsb5exy.cloudfront.net/myjobs/data/usa_regions.json'
    data_list = json.loads(urllib2.urlopen(data_url).read())['regions']
    state_map = dict([(x['name'], x['code']) for x in data_list])
    state_map['None'] = 'None'
    return state_map


# A dict that maps state names and their abbreviations to valid synonyms. For
# example, synonyms['IN'] and synonyms['Indiana'] both return ['IN',
# 'Indiana'].
synonyms = dict(
    [(key.lower(), [key, value]) for key, value in get_state_map().items()] +
    [(value.lower(), [key, value]) for key, value in get_state_map().items()])
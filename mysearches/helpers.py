import json
import urllib2
from bs4 import BeautifulSoup
from urlparse import urlparse, urlunparse, parse_qs
from urllib import urlencode
from dateutil import parser as dateparser
import datetime

from django.utils import simplejson
from django.utils.encoding import smart_str, smart_unicode

from myprofile.models import SecondaryEmail


def validate_dotjobs_url(search_url):
    """
    Validate (but not parse) a .jobs URL. Nothing is returned if the URL has no
    no rss link is found. Only the title is returned if the rss url is invalid.

    Inputs:
    :search_url:   URL to be validated

    Outputs:
    :title:        The title attribute taken from the rss link
    :rss_url:      The href attribute taken from the rss link
    """
    if not search_url:
        return None, None

    if search_url.find('://') == -1:
        search_url = "http://" + search_url

    try:
        soup = BeautifulSoup(urllib2.urlopen(search_url).read(), "html.parser")
    except:
        return None, None
    link = soup.find("link", {"type":"application/rss+xml"})

    if link:
        title = link.get('title')
        rss_url = link.get('href')
        try:
            params = ''
            if rss_url.find('?') == -1:
                params += '?num_items=1'
            else:
                params += '&num_items=1'
            rss_soup = get_rss_soup(rss_url+params)
        except:
            return title, None
        return title, rss_url
    else:
        return None, None


def get_rss_soup(rss_url):
    """
    Turn a URL into a BeatifulSoup object
    
    Inputs:
    :rss_url:      URL of an RSS feed

    Outputs:
                   BeautifulSoup object
    """

    rss_feed = urllib2.urlopen(rss_url).read()
    return BeautifulSoup(rss_feed, "html.parser")


def get_json(json_url):
    """
    Turn a remote json file into a Python dictionary

    Inputs:
    :json_url:    URL of a json file

    Outputs:
                    List of one or more Python dictionaries
    """
    json_feed = urllib2.urlopen(json_url).read()
    return json.loads(json_feed)



def parse_feed(feed_url, frequency='W', num_items=20, offset=0):
    """
    Parses job data from an RSS feed and returns it as a list of dictionaries.
    The data returned is limited based on the corresponding data range (daily,
    weekly, or monthly).

    Inputs:
    :feed_url:      URL of an RSS feed
    :frequency:     String 'D', 'W', or 'M'.
    :num_items:     Maximum number of items to be returned.
    :offset:        The page on which the RSS feed is on.

    Outputs:
    :item_list:     List of dictionaries of job data. Each dictionary contains
                    the job title, description, link to the .jobs page, and
                    publish date.
    """
    if feed_url.find('?') > -1:
        separator = '&'
    else:
        separator = '?'
    feed_url = feed_url.replace('feed/rss', 'feed/json')

    interval = get_interval_from_frequency(frequency)

    end = datetime.date.today()
    start = end + datetime.timedelta(days=interval)
    item_list = []

    feed_url += '%snum_items=%s&offset=%s' % (
        separator, str(num_items), str(offset))

    if 'feed/json' in feed_url:
        try:
            json_feed = get_json(feed_url)
        except ValueError:
            json_feed = []

        count = len(json_feed)

        for item in json_feed:
            item['link'] = item['url']
            del item['url']

            item['pubdate'] = dateparser.parse(item['date_new'])
            del item['date_new']

            if date_in_range(start, end, item['pubdate'].date()):
                item_list.append(item)
            else:
                break

            if len(item_list) == 5:
                break
    else:
        rss_soup = get_rss_soup(feed_url)
        items = rss_soup.find_all("item")
        count = len(items)

        for item in items:
            item_dict = {}
            item_dict['title'] = item.findChild('title').text
            item_dict['link'] = item.findChild('link').text
            item_dict['pubdate'] = dateparser.parse(item.findChild('pubdate').text)
            item_dict['description'] = item.findChild('description').text

            if date_in_range(start,end,item_dict['pubdate'].date()):
                item_list.append(item_dict)
            else:
                break

            if len(item_list) == 5:
                break

    return item_list, count


def date_in_range(start, end, x):
    return start <= x <= end


def url_sort_options(feed_url, sort_by, frequency=None):
    """
    Updates urls based on sort by option. 

    Inputs:
    :feed_url:      URL of an RSS feed 
    :sort_by:       What the feed should be sorted by ('Relevance' or 'Date')
    :frequency:     Frequency of saved search ('D', 'W', 'M')

    Output:
    :feed_url:      URL updated with sorting options. 'Date' has no additions to
                    the URL and  'Relevance' should has '&date_sort=False' added
    """

    # If unicode is present in the string, escape it
    feed = smart_str(feed_url)
    unparsed_feed = urlparse(feed)
    query = parse_qs(unparsed_feed.query)
    query.pop('date_sort', None)


    if sort_by == "Relevance":
        query.update({'date_sort': 'False'})

        interval = -get_interval_from_frequency(frequency)

        query.update({'days_ago': interval})

    unparsed_feed = unparsed_feed._replace(query = urlencode(query, True))
    # Convert byte string back into unicode
    feed_url = smart_unicode(urlunparse(unparsed_feed))

    return feed_url


def get_interval_from_frequency(frequency):
    intervals = {'D': -1,
                 'W': -7,
                 'M': -30}
    return intervals.get(frequency, -1)


# -*- coding: utf-8 -*-
import datetime
from urlparse import urlparse, parse_qs

from django.conf import settings
from django.contrib.auth.models import Group

from mock import patch

from myjobs.tests.setup import MyJobsBase
from mysearches.models import SavedSearch
from mysearches.helpers import (date_in_range, parse_feed,
                                update_url_if_protected, url_sort_options,
                                validate_dotjobs_url)

from mysearches.tests.helpers import return_file
from myjobs.tests.factories import UserFactory


class SavedSearchHelperTests(MyJobsBase):
    def setUp(self):
        super(SavedSearchHelperTests, self).setUp()
        self.user = UserFactory()
        self.valid_url = 'http://www.my.jobs/jobs?location=chicago&q=nurse'

        self.patcher = patch('urllib2.urlopen', return_file())
        self.patcher.start()

    def tearDown(self):
        super(SavedSearchHelperTests, self).tearDown()
        self.patcher.stop()

    def test_valid_dotjobs_url(self):
        url, soup = validate_dotjobs_url(self.valid_url, self.user)
        self.assertIsNotNone(url)
        self.assertIsNotNone(soup)

        no_netloc = 'www.my.jobs/jobs?location=chicago&q=nurse'
        title, url = validate_dotjobs_url(no_netloc, self.user)
        self.assertIsNotNone(title)
        self.assertIsNotNone(url)
        expected = urlparse(
            'http://www.my.jobs/jobs/feed/rss?q=nurse&location=chicago')
        actual = urlparse(url.replace('amp;', ''))
        self.assertEqual(actual.path, expected.path)
        self.assertEqual(parse_qs(actual.query), parse_qs(expected.query))

        valid_filter_url = 'www.my.jobs/jobs/'
        title, url = validate_dotjobs_url(valid_filter_url, self.user)
        self.assertIsNotNone(title)
        self.assertIsNotNone(url)

    def test_validate_dotjobs_url_with_special_chars(self):
        urls = [
            ('http://www.my.jobs/jobs/?q=query with spaces/',
             'http://www.my.jobs/jobs/feed/rss?q=query+with+spaces'),
            ('http://www.my.jobs/jobs/?q=яы',
             'http://www.my.jobs/jobs/feed/rss?q=%D1%8F%D1%8B')
        ]
        for url_set in urls:
            label, feed = validate_dotjobs_url(url_set[0], self.user)
            self.assertEqual(feed, url_set[1])
            self.assertIsNotNone(label)

    def test_invalid_dotjobs_url(self):
        urls = ['http://google.com',  # url does not contain a feed
                '',  # url not provided
                'http://']  # invalid url provided
        for url in urls:
            title, url = validate_dotjobs_url(url, self.user)
            self.assertIsNone(title)
            self.assertIsNone(url)

    def test_date_in_range(self):
        start = datetime.date(month=1, day=1, year=2013)
        end = datetime.date(month=12, day=1, year=2013)
        x = datetime.date(month=6, day=1, year=2013)
        is_in_range = date_in_range(start, end, x)
        self.assertTrue(is_in_range)

        start = datetime.date(month=1, day=1, year=2013)
        end = datetime.date(month=12, day=1, year=2013)
        x = datetime.date(month=6, day=1, year=2010)
        is_in_range = date_in_range(start, end, x)
        self.assertFalse(is_in_range)

    def test_parse_feed(self):
        feed_url = 'http://www.my.jobs/feed/rss'

        for use_json, count in [(True, 2), (False, 1)]:
            items = parse_feed(feed_url, use_json=use_json)

            # The second value in the items list is the total count from a
            # feed, which may not equal the number of items returned
            self.assertEqual(items[1], len(items[0]))
            item = items[0][0]
            for element in ['pubdate', 'title', 'description', 'link']:
                self.assertTrue(item[element])

    def test_parse_feed_with_count(self):
        feed_url = 'http://www.my.jobs/feed/rss'
        num_items = 1

        items, count = parse_feed(feed_url, num_items=num_items)
        self.assertEqual(count, num_items)

    def test_url_sort_options(self):
        feed = 'http://www.my.jobs/jobs/feed/rss?date_sort=False'

        # Test to make sure sort by "Relevance" has '&date_sort=False' added
        # a single time
        feed_url = url_sort_options(feed, "Relevance")
        parsed = urlparse(feed_url)
        query = parse_qs(parsed.query)
        self.assertEquals(parsed.path, "/jobs/feed/rss")
        self.assertEquals(query['date_sort'], [u'False'])
        # If a frequency isn't specified, days_ago should be missing from
        # the url.
        self.assertNotIn('days_ago', query)
    
        # Test to make sure sort by "Date" doesn't have anything added
        feed_url = url_sort_options(feed, "Date")
        self.assertEquals(feed_url, "http://www.my.jobs/jobs/feed/rss")

        # Test to make sure that passing in a frequency does in fact
        # add the frequency to the feed url.
        feed_url = url_sort_options(feed, "Relevance", frequency='D')
        query = parse_qs(urlparse(feed_url).query)
        self.assertEquals(query['days_ago'][0], '1')
        feed_url = url_sort_options(feed, "Relevance", frequency='W')
        query = parse_qs(urlparse(feed_url).query)
        self.assertEquals(query['days_ago'][0], '7')
        feed_url = url_sort_options(feed, "Relevance", frequency='M')
        query = parse_qs(urlparse(feed_url).query)
        self.assertEqual(query['days_ago'][0], '30')

    def test_unicode_in_search(self):
        search = SavedSearch(url=u"http://www.my.jobs/search?q=%E2%80%93",
                             user=self.user,
                             feed=u"http://www.my.jobs/search/feed/rss?q=%E2%80%93",
                             sort_by=u'Relevance')
        search.save()

        feed_url = url_sort_options(search.feed, search.sort_by)

        old = parse_qs(urlparse(search.feed).query)
        new = parse_qs(urlparse(feed_url).query)

        self.assertFalse(old.get('date_sort'))
        self.assertTrue(new['date_sort'][0])

        del new['date_sort']
        self.assertEqual(new, old)

    def test_feed_on_protected_site_no_access(self):
        from mydashboard.tests.factories import SeoSiteFactory
        site_id = settings.PROTECTED_SITES.keys()[0]
        site = SeoSiteFactory(pk=site_id, id=site_id)

        url = "http://%s?q=query" % site.domain
        result = update_url_if_protected(url, self.user)
        self.assertEqual(result, url)

    def test_feed_on_protected_site_with_access(self):
        from mydashboard.tests.factories import SeoSiteFactory
        site_id = settings.PROTECTED_SITES.keys()[0]
        site = SeoSiteFactory(pk=site_id, id=site_id)
        group_id = settings.PROTECTED_SITES.values()[0][0]
        Group.objects.create(pk=group_id, name='Test Group')

        self.user.groups.add(group_id)
        self.user.save()

        url = "http://%s?q=query" % site.domain
        expected_result = "%s&key=%s" % (url, settings.SEARCH_API_KEY)
        result = update_url_if_protected(url, self.user)
        self.assertEqual(result, expected_result)

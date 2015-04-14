from datetime import datetime
from itertools import chain, combinations
import json
import re

from api.helpers import simple_api_fields
from api.models import CityToCentroidMapping, Search
from api.tests.setup import BaseTestCase


class Views(BaseTestCase):
    def test_individual_query_parameters(self):
        """
        Test confirms that all individual query parameters are not causing
        any errors.

        """
        path = self.path
        for value in self.search_mapping:
            path += "%s=%s&" % (value, self.search_mapping[value])
            response = self.client.get(path)

            self.assertEqual(response.status_code, 200)
            self.assertNotIn('Search too broad', response.content)

    def test_query_parameter_combinations(self):
        """
        Test confirms that combinations of query parameters are not causing
        any errors.

        """
        # Create a list of all the combinations of keys
        keys = ['onet', 'tm', 'ind', 'cn', 'zc', 'zc1', 'rd1', 'cname', 'i',
                'moc', 'branch']
        naive_combos = chain.from_iterable(combinations(keys, r)
                                           for r in range(1, len(keys) + 1))
        # Filter that list to prevent zd1 being sent without zc1
        combos = []
        for combo in naive_combos:
            if 'rd1' in combo and 'zc1' not in combo:
                continue
            combos.append(combo)

        for combo in combos:
            path = self.path
            for param in combo:
                path += "%s=%s&" % (param, self.search_mapping[param])

            response = self.client.get(path)

            self.assertEqual(response.status_code, 200)
            self.assertNotIn('Query format error', response.content)

    def test_blank_query_value(self):
        """
        Test confirms that blank query parameters do not cause any errors.

        """
        path = '%sonet=&tm=1' % self.path
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Search too broad', response.content)
        self.assertNotIn('Query format error', response.content)

    def test_blank_query(self):
        """
        Test checks for 'Search too broad' error when no query parameters
        are present.

        """
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, 400)
        self.assertIn('Search too broad', response.content)

    def test_cntl(self):
        """
        Test checks to see if cntl formatting is being applied when flag is
        present and not applied otherwise.

        """
        path = '%stm=10&cntl=1' % self.countspath
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertIn('<counts>', response.content)

        path = '%stm=10&cntl=0' % self.countspath
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('<counts>', response.content)

    def test_rc(self):
        """
        Test checks to see if rc formatting is being applied when flag is
        present and not applied otherwise.

        """
        path = '%sonet=%s&rc=1' % (self.countspath, self.fixture_onets)
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertIn('<onet>12345678</onet>', response.content)
        self.assertIn('<recordcount>1</recordcount>', response.content)

        path = '%sonet=%s&rc=1' % (self.countspath, self.fixture_onets)
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('<recordcount>2</recordcount>', response.content)
        self.assertNotIn('<recordcounts>', response.content)
        self.assertIn('<item>', response.content)

        path = '%sonet=*&rc=0' % self.countspath
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertIn('<recordcount>2</recordcount>', response.content)
        self.assertNotIn('<item>', response.content)

    def test_countsapi_no_rc_or_cntl(self):
        path = '%stm=99999' % self.countspath
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertIn('</fc>', response.content)
        self.assertIn('</onet>', response.content)

    def test_scope(self):
        """
        Test confirms that users with scope '7' (network only) aren't
        seeing all jobs.

        """
        test_onet = 13201101
        not_network = {'buid': '77', 'id': '12345', 'guid': '123456',
                       'onet': test_onet, 'network': 'false',
                       'date_new': datetime.now()}
        self.solr.add([not_network])
        path = '%sonet=%s' % (self.path, test_onet)
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        # Users with scope 'all' should see both all jobs with test_onet
        self.assertIn('<recordcount>2</recordcount>', response.content)

        self.user.scope = '7'
        self.user.save()
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        # Users with scope 'network only' should only see the jobs
        # where network == true
        self.assertIn('<recordcount>1</recordcount>', response.content)

    def test_industry(self):
        """
        Confirms that industry ids are being correctly translated to industries
        during search.

        """
        path = '%sind=1' % self.path
        response = self.client.get(path)

        self.assertIn("Consumer Services", response.content)

    def test_search_id_creation(self):
        """
        Search ids are being properly added and used.

        """
        time = re.compile('<time>.*</time>')

        path = '%skw=keyword&cname=company&zc=01234' % self.path
        response = self.client.get(path)
        old_content = re.sub(time, response.content, '')

        # A search id is being created
        search = Search.objects.get(user=self.user)
        self.assertIn('<id>%s</id>' % search.id, response.content)

        path = "%ssi=%s" % (self.path, search.id)
        response = self.client.get(path)
        # A search for an old search doesn't generate a new search id
        new_content = re.sub(time, response.content, '')
        self.assertIn('<id>%s</id>' % search.id, response.content)
        Search.objects.get(user=self.user)

        # The same search id should result in the same page
        self.assertEqual(old_content, new_content)

        path = "%ssi=1&branch=army" % self.path
        response = self.client.get(path)
        # A search based on an old search does not generate a new search id
        self.assertIn('<id>%s</id>' % search.id, response.content)
        self.assertEqual(Search.objects.filter(user=self.user).count(), 1)

        path = "%sbranch=army" % self.path
        self.client.get(path)
        # Another brand new search should generate another brand new search id
        self.assertEqual(Search.objects.filter(user=self.user).count(), 2)

    def test_invalid_search_id(self):
        path = "%ssi=999999" % self.path
        response = self.client.get(path)

        self.assertIn('<error>Search matching id does not exist</error>',
                      response.content)
        self.assertEqual(response.status_code, 400)

    def test_search_param_updates(self):
        """
        Confirms that searches based on search id are getting the updated
        solr parameters if there are any.

        """
        path = "%skw=keyword&cname=company" % self.path
        self.client.get(path)
        search = Search.objects.get(user=self.user)

        path = "%ssi=%s&kw=another keyword&cname=company2" % (self.path,
                                                              search.id)

        response = self.client.get(path)
        self.assertIn('<query>another keyword for company2</query>',
                      response.content)
        self.assertIn('<id>%s</id>' % search.id, response.content)

    def test_description(self):
        """
        Description should not be given unless requested.

        """
        path = "%skw=*" % self.path
        response = self.client.get(path)
        self.assertNotIn('<Description>', response.content)

        path = '%sjvid=%s' % (self.path, self.fixture_jvid)
        response = self.client.get(path)
        self.assertIn('<Description>', response.content)

    def test_jvid_access(self):
        """
        Only specific users should have access to the jvid view.

        """
        # By default the factory user has jvid access turned on
        path = '%sjvid=%s' % (self.path, self.fixture_jvid)
        response = self.client.get(path)
        self.assertNotIn('<error>Job No Longer Available</error>',
                         response.content)

        self.user.jv_api_access = 0
        self.user.save()
        response = self.client.get(path)
        self.assertIn('<error>Job No Longer Available</error>',
                      response.content)

    def test_onet_access(self):
        """
        Only specific users should have access to the onet on jobs.

        """
        # By default the factory user has onet access turned on.
        path = "%sjvid=%s" % (self.path, self.fixture_jvid)
        response = self.client.get(path)
        self.assertIn('</Onet>', response.content)

        self.user.onet_access = 0
        self.user.save()
        response = self.client.get(path)
        self.assertNotIn('</Onet>', response.content)

        # Users without onet access should still be able to get onet
        # counts.
        path = '%sonets=12345678&rc=1' % self.countspath
        response = self.client.get(path)
        self.assertIn('</onet>', response.content)

    def test_zc_zc1(self):
        def assert_guid():
            self.assertIn('<jvid>0F21D879F4904BDB90EC27A3843A1B091</jvid>',
                          response.content)

        def assert_count():
            self.assertIn('<recordcount>1</recordcount>', response.content)

        # zc and zc1 fields should alone yeild the correct search result.
        expected_query = '<query>in 07054</query>'
        path = "%szc=%s" % (self.path, '07054')
        response = self.client.get(path)
        assert_count()
        self.assertIn(expected_query, response.content)
        assert_guid()

        expected_query = '<query>in 07054 (within 25 miles)</query>'
        path = "%szc1=%s" % (self.path, '07054')
        response = self.client.get(path)
        assert_count()
        self.assertIn(expected_query, response.content)
        assert_guid()

        # Having an empty zc or zc1 field should not impact the search
        # result.
        expected_query = '<query>in 07054</query>'
        path = "%szc=%s&zc1=" % (self.path, '07054')
        response = self.client.get(path)
        assert_count()
        self.assertIn(expected_query, response.content)
        assert_guid()

        expected_query = '<query>in 07054 (within 25 miles)</query>'
        path = "%szc1=%s&zc=" % (self.path, '07054')
        response = self.client.get(path)
        assert_count()
        self.assertIn(expected_query, response.content)
        assert_guid()

        # Just a city name should work in both.
        expected_query = '<query>in Parsippany</query>'
        path = "%szc=%s" % (self.path, 'Parsippany')
        response = self.client.get(path)
        assert_count()
        self.assertIn(expected_query, response.content)
        assert_guid()

        path = "%szc1=%s" % (self.path, 'Parsippany')
        response = self.client.get(path)
        assert_count()
        self.assertIn(expected_query, response.content)
        assert_guid()

        # City, State combo should work in both.
        expected_query = '<query>in Parsippany, New Jersey</query>'
        path = "%szc=%s" % (self.path, 'Parsippany, New Jersey')
        response = self.client.get(path)
        assert_count()
        self.assertIn(expected_query, response.content)
        assert_guid()

        path = "%szc1=%s" % (self.path, 'Parsippany, New Jersey')
        response = self.client.get(path)
        assert_count()
        self.assertIn(expected_query, response.content)
        assert_guid()

        # City, State combo should also work in both when there is a valid
        # CityToCentroidMapping for the location.
        CityToCentroidMapping.objects.create(city='Parsippany',
                                             state='New Jersey',
                                             centroid_lat='40.859388',
                                             centroid_lon='-74.413425')
        expected_query = '<query>in Parsippany, New Jersey</query>'
        path = "%szc=%s" % (self.path, 'Parsippany, New Jersey')
        response = self.client.get(path)
        assert_count()
        self.assertIn(expected_query, response.content)
        assert_guid()

        expected_query = '<query>in Parsippany, New Jersey (within 25 miles)</query>'
        path = "%szc1=%s" % (self.path, 'Parsippany, New Jersey')
        response = self.client.get(path)
        self.assertIn(expected_query, response.content)
        assert_guid()

    def test_onet_clean(self):
        def assert_title():
            self.assertIn('<query>onet-title</query>', response.content)

        def assert_count():
            self.assertIn('<recordcount>1</recordcount>', response.content)

        # Cleaned onet gets the expected result.
        path = "%sonets=%s" % (self.path, self.fixture_onets)
        response = self.client.get(path)
        assert_title()
        assert_count()

        # Onet with . and - also gets the expected result.
        onet = "%s-%s.%s" % (self.fixture_onets[:2], self.fixture_onets[2:-2],
                             self.fixture_onets[-2:])
        path = "%sonets=%s" % (self.path, onet)
        response = self.client.get(path)
        assert_title()
        assert_count()

    def test_onet_wildcarding(self):
        onet = "%s000000" % self.fixture_onets[:2]
        path = "%sonets=%s" % (self.path, onet)
        response = self.client.get(path)
        self.assertIn('<jvid>0F21D879F4904BDB90EC27A3843A1B091</jvid>',
                      response.content)
        self.assertIn('<recordcount>1</recordcount>',
                      response.content)
        # Because the onet has been wildcarded, we can't match the
        # onet title correctly so there won't be a matching query.
        self.assertIn('<query></query>', response.content)

    def test_kw_in_query(self):
        path = "%skw=%s" % (self.path, 'KEYWORD')
        self.client.get(path)

        search = Search.objects.get()
        self.assertIn('KEYWORD', search.query)
        self.assertNotIn('KEYWORD', json.loads(search.solr_params)['fq'])

    def test_blank_fields(self):
        fields = "=&".join(simple_api_fields)
        path = "%s%s=" % (self.path, fields)
        response = self.client.get(path)

        self.assertIn("Search too broad", response.content)
        self.assertEqual(response.status_code, 400)

    def test_bad_search_id(self):
        bad_search_ids = ['a', 46546, 'asdfadsf', 3.5]
        for bad_id in bad_search_ids:
            path = "%ssi=%s" % (self.path, bad_id)
            response = self.client.get(path)
            self.assertIn('Search matching id does not exist', response.content)

    def test_onet_count_zero(self):
        onets = ['65161', '156168091681', '8946161331', '86515']
        path = "%sonets=%s&rc=1" % (self.countspath, ", ".join(onets))
        response = self.client.get(path)

        for onet in onets:
            self.assertIn('<onet>%s</onet>' % onet.strip(), response.content)
        self.assertIn('<recordcount>0</recordcount>', response.content)

    def test_rows(self):
        def get_path(start, end):
            return "%skw=*&rs=%s&re=%s" % (self.path, str(start), str(end))

        def compare(start, expected_start, end, expected_end, expected_count):
            response = self.client.get(get_path(start, end))
            self.assertIn('<startrow>%s</startrow>' % expected_start,
                          response.content)
            self.assertIn('<endrow>%s</endrow>' % expected_end,
                          response.content)
            self.assertEqual(response.content.count('<job>'), expected_count)

        # Load 1000 useless jobs
        jobs = []
        for x in range(1, 1000):
            jobs.append({
                'title': 'Title',
                'link': 'http://my.jobs/%s/' % str(x)*32,
                'guid': str(x)*32,
                'id': x,
                'company': 'Company',
                'city': 'Indianapolis',
                'state': 'IN',
                'date_new': datetime.now(),
                'federal_contractor': False,
                'text': 'Title'
            })
        self.solr.add(jobs)

        compare(-1, 1, -1, 1, 1)
        compare(1, 1, 1, 1, 1)
        compare(1, 1, 2, 2, 2)
        compare(2, 2, 1, 11, 10)
        compare(0, 1, 1000, 500, 500)
        compare(5, 5, 10, 10, 6)

        path = "%skw=*" % self.path
        response = self.client.get(path)
        self.assertIn('<startrow>1</startrow>', response.content)
        self.assertIn('<endrow>10</endrow>', response.content)
        self.assertEqual(response.content.count('<job>'), 10)

        path = "%skw=*&rs=5" % self.path
        response = self.client.get(path)
        self.assertIn('<startrow>5</startrow>', response.content)
        self.assertIn('<endrow>14</endrow>', response.content)
        self.assertEqual(response.content.count('<job>'), 10)

        path = "%skw=*&re=50" % self.path
        response = self.client.get(path)
        self.assertIn('<startrow>1</startrow>', response.content)
        self.assertIn('<endrow>50</endrow>', response.content)
        self.assertEqual(response.content.count('<job>'), 50)
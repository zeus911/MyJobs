"""Tests associated with myreports helpers."""

import csv
import json
from cStringIO import StringIO
from django.test.client import RequestFactory

from mypartners.tests.factories import ContactRecordFactory, TagFactory
from mypartners.models import ContactRecord
from myreports.tests.test_views import MyReportsTestCase
from myreports import helpers


class TestHelpers(MyReportsTestCase):
    def setUp(self):
        super(TestHelpers, self).setUp()

        tags = [TagFactory(name=name, company=self.company) for name in [
            'test', 'stuff', 'working']]

        # Returns a list rather than a QuerySet, which is what the helper
        # functions use, so saving this to a variable isn't really helpful
        ContactRecordFactory.create_batch(
            10, partner=self.partner, contact_name='Joe Shmoe', tags=tags)

        self.records = ContactRecord.objects.all()

    def test_serialize_python(self):
        """
        Test that serializing a `QuerySet` into a Python object creates the
        correct number of `dict`s.
        """

        data = helpers.serialize('python', self.records)

        self.assertEqual(len(data), self.records.count())

    def test_serialize_json(self):
        """
        Test that serializing to JSON creates the correct number of
        objects.
        """

        # JSON is returned as a string, but deserializing it after serializing
        # it should create a list of dicts comparable to the number of records
        # that actually exist.
        data = json.loads(helpers.serialize('json', self.records))

        self.assertEqual(len(data), self.records.count())

    def test_serialize_csv(self):
        """Test that serializing to CSV creates the correct number of rows."""

        data = StringIO(helpers.serialize('csv', self.records))
        reader = csv.reader(data, delimiter=',')

        self.assertEqual(len(list(reader)) - 1, self.records.count())

    def test_humanize(self):
        """Test that fields get converted to human-readable equivalents."""

        data = helpers.humanize(helpers.serialize('python', self.records))

        for record in data:
            # ensure tags were converted
            self.assertEqual(record['tags'], 'test, stuff, working')

            # ensure pk was removed
            self.assertFalse('pk' in record.keys())

            # ensure contact type was converted
            self.assertTrue(record['contact_type'] == 'Email')

    def test_parse_params(self):
        """Test that params are properly parsed from a `QueryDict`."""

        factory = RequestFactory()
        request = factory.post(
            '/reports/view/mypartners/contact',
            data=dict(
                foo=['bar', 'baz'],
                buz=['biz'],
                quz='fizz'
            ))

        params = helpers.parse_params(request.POST)

        # Singleton lists should be flattened into single elements, lists
        # should be converted to tuples, and already flat elements should
        # remain untouched.
        self.assertEqual(
            params, dict(buz='biz', quz='fizz', foo=('bar', 'baz')))

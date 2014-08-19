from itertools import product
from datetime import datetime, timedelta

import pytz
from django.db.models import Min, Max

from mypartners import helpers
from mypartners.tests.test_views import MyPartnersTestCase


class HelpersTests(MyPartnersTestCase):

    def test_find_partner_from_email(self):
        email_and_expected_partner = [
            ('someone@my.jobs', self.partner),
            ('someone@www.my.jobs', self.partner),
            ('someone@notmy.jobs', None),
            (None, None),
        ]
        for email, expected_partner in email_and_expected_partner:
            partner = helpers.find_partner_from_email([self.partner], email)
            self.assertEqual(partner, expected_partner)

    def test_find_partner_from_email_no_partners(self):
        partner = helpers.find_partner_from_email(None, 'someone@my.jobs')
        self.assertIsNone(partner)

    def test_get_records_from_request_with_date(self):
        """ Make sure that the number of days shown in the date drop dwon
            matches the what was selected by user"""

        record_types = ["email", "phone", "meetingorevent"]
        date = ["0", "1", "30", "90", ""]

        params = product(record_types, date)

        for record_type, date in params:
            request = self.request_factory.get(
                'prm/view/reports/details/records/', dict(
                    company=self.company.id,
                    partner=self.partner.id,
                    record_type=record_type,
                    date=date,
                    )
                )
            request.user = self.staff_user

            response = helpers.get_records_from_request(request)
            (range_start, range_end), date_str, records = response

            expected = date_str.split()[0].lstrip("-")

            if expected.isdigit():
                days = int(expected)
                if days == 1:
                    self.assertEqual("1 Day", date_str)
                else:
                    self.assertEqual(
                        "%i Days" % (range_end - range_start).days, date_str)
            else:
                self.assertEqual("View All", date_str)

    def test_start_date_before_end_date(self):
        request = self.request_factory.get(
            'prm/view/reports/details/records/', dict(
                company=self.company.id,
                partner=self.partner.id,
                range_start='02/15/14',
                range_end='04/15/12'))
        request.user = self.staff_user

        response = helpers.get_records_from_request(request)
        (start_date, end_date), _, _ = response
        self.assertGreaterEqual(end_date, start_date)


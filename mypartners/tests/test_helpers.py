from itertools import chain, product, islice
from datetime import datetime, timedelta
import os
import random

import pytz
from django.db.models import Min, Max

from tasks import update_partner_library
from mypartners import helpers, models
from mypartners.helpers import get_library_partners, new_partner_from_library
from mypartners.tests.test_views import (MyPartnersTestCase, 
                                         PartnerLibraryTestCase)


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


class PartnerLibraryFilterTests(PartnerLibraryTestCase):

    def test_all_offcp_partners_available(self):
        """
        When a company doesn't have any OFCCP partners, they should all be
        available to choose from in the partner library search.
        """
        partner_count = self.partner_library.count()
        request = self.request_factory.get(
            'prm/view/partner-library/', dict(company=self.company.id))

        response = helpers.filter_partners(request, partner_library=True)

        self.assertEqual(len(response), partner_count)

    def test_ofccp_duplicates_ignored(self):
        """
        When a company has already added OFCCP partners, those partners should
        not be displayed in the filter search results.
        """

        # create a new partner
        library_id = random.randint(1, self.partner_library.count())
        request = self.request_factory.get(
            'prm/view/partner-library/add', dict(
                company=self.company.id, library_id=library_id))
        request.user = self.staff_user
        partner = helpers.new_partner_from_library(request)

        # get a list of OFCCP partners
        request = self.request_factory.get(
            'prm/view/partner-library', dict(company=self.company.id))
        request.user = self.staff_user
        library = helpers.filter_partners(request, partner_library=True)

        self.assertFalse(library.filter(id=partner.library.id).exists())

    def test_keyword_filter(self):
        """
        When a user tries to filter using keywords, the partner name, partner
        URI, and contact name should be searched.
        """

        request = self.request_factory.get(
            'prm/view/partner-library/', dict(
                company=self.company.id,
                keywords='center, .org'))
        request.user = self.staff_user

        response = helpers.filter_partners(request, partner_library=True)
        self.assertTrue(len(response) != 0)

        for partner in response:
            searchable_fields = " ".join(
                [partner.name, partner.uri, partner.contact_name]).lower()

            self.assertIn('center', searchable_fields)
            self.assertIn('.org', searchable_fields)

    def test_state_filter(self):
        """
        Filter by state.
        """

        request = self.request_factory.get(
            'prm/view/partner-library/', dict(
                company=self.company.id,
                state='PA'))
        request.user = self.staff_user

        response = helpers.filter_partners(request, partner_library=True)
        self.assertTrue(len(response) != 0)

        for partner in response:
            self.assertEqual(partner.st, 'PA')

    def test_city_filter(self):
        """
        Filter by city.
        """

        print [partner.city for partner in self.partner_library]
        request = self.request_factory.get(
            'prm/view/partner-library/', dict(
                company=self.company.id,
                city='Monaco'))
        request.user = self.staff_user

        response = helpers.filter_partners(request, partner_library=True)
        self.assertTrue(len(response) != 0)

        for partner in response:
            self.assertEqual(partner.city, 'Monaco')
    
    

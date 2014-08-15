from itertools import product, islice
from datetime import datetime, timedelta
import os
import random

import pytz
from django.db.models import Min, Max

from tasks import update_partner_library
from mypartners import helpers, models
from mypartners.helpers import get_library_partners
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


class PartnerFilterTests(MyPartnersTestCase):

    """
    Tests related to filter_partners. 
    """

    @classmethod
    def setUpClass(cls):
        super(PartnerFilterTests, cls).setUpClass()
        path = os.path.join(
            os.path.dirname(__file__), 'data', 'partner-library.html')
        for partner in islice(get_library_partners(path), 0, 10):
            fullname = " ".join(" ".join([partner.first_name,
                                          partner.middle_name,
                                          partner.last_name]).split())

            if not models.PartnerLibrary.objects.filter(
                    contact_name=fullname, st=partner.st, city=partner.city):
                models.PartnerLibrary(
                    name=partner.organization_name, uri=partner.website,
                    region=partner.region, state=partner.state, 
                    area=partner.area, contact_name=fullname,
                    phone=partner.phone, phone_ext=partner.phone_ext,
                    alt_phone=partner.alt_phone, fax=partner.fax,
                    email=partner.email_id, street1=partner.street1,
                    street2=partner.street2, city=partner.city, st=partner.st,
                    zip_code=partner.zip_code, is_minority=partner.minority,
                    is_female=partner.female, is_disabled=partner.disabled,
                    is_disabled_veteran=partner.disabled_veteran,
                    is_veteran=partner.veteran).save()
        cls.partner_library = models.PartnerLibrary.objects.all()

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
        pass

        




from mypartners.helpers import find_partner_from_email
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
            partner = find_partner_from_email([self.partner], email)
            self.assertEqual(partner, expected_partner)

    def test_find_partner_from_email_no_partners(self):
        partner = find_partner_from_email(None, 'someone@my.jobs')
        self.assertIsNone(partner)

from django.test import TestCase

from mydashboard.templatetags.humanize_abbr import intabbr


class HumanizeAbbrTests(TestCase):
    def test_small_numbers(self):
        for in_val in [-1000, -1, 0, 1, 999]:
            self.assertEqual(intabbr(in_val), in_val)

    def test_large_numbers(self):
        for in_tuple in [(1000, '1.0k'), (1100, '1.1k'),
                         (999000, '999.0k'), (999999, '999.9k'),
                         (1000000, '1.0M'), (10000000000, '10.0B')]:
            self.assertEqual(intabbr(in_tuple[0]), in_tuple[1])

from django.conf import settings


from seo.models import SeoSite
from seo.tests.setup import DirectSEOBase
from social_links.models import SocialLinkType
from social_links.tests.factories import (SocialLinkFactory,
                                          SocialLinkTypeFactory)


class SocialLinksModelsTetCase(DirectSEOBase):
    def tearDown(self):
        for social_link_type in SocialLinkType.objects.all():
            social_link_type.delete()

    def test_get_canonical_icon_link(self):
        """
        Non-manually-uploaded social icons start with either the bare
        cloudfront url or png.nlx.org. Manually-uploaded social icons are just
        the file path. Ensure we get the correct computed link in each case.
        """
        settings.DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
        s3_url = '//d2e48ltfsb5exy.cloudfront.net'
        png_url = 'http://png.nlx.org'
        for index, expected_icon in enumerate(['%s/icon/icon.png' % url
                                               for url in [s3_url, s3_url,
                                                           png_url]]):
            link_icon = expected_icon.replace(s3_url, '') if index == 0\
                else expected_icon
            social_link = SocialLinkFactory(link_icon=link_icon)
            site = SeoSite.objects.get(pk=1)
            social_link.sites.add(site)

            computed_icon = social_link.get_icon()
            self.assertEqual(computed_icon, expected_icon)


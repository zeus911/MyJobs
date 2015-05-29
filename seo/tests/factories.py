import factory
import factory.django
import factory.fuzzy
from slugify import slugify

from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

from myjobs.tests.factories import UserFactory
from seo.models import SeoSiteFacet

copy_to_database = 'qc-redirect'


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.fuzzy.FuzzyText("Test")


class GroupCopyToFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
        database = copy_to_database

    name = factory.fuzzy.FuzzyText("Test")


class SiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Site

    domain = 'buckconsultants.jobs'
    name = u'buckconsultants.jobs'


class GoogleAnalyticsCampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.GoogleAnalyticsCampaign'

    name = 'Test'
    group = factory.SubFactory(GroupFactory)


class BusinessUnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.BusinessUnit'

    id = factory.fuzzy.FuzzyInteger(1, high=99999)
    title = "Panasonic"
    title_slug = factory.LazyAttribute(lambda x: slugify(x.title))
    federal_contractor = True
    date_updated = "2010-10-18 10:59:24"
    associated_jobs = 4
    date_crawled = "2010-10-18 07:00:02"
    enable_markdown = True


class GACampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.GoogleAnalyticsCampaign'

    name = "Test Google Analytics Campaign"
    group = factory.SubFactory(GroupFactory)
    campaign_source = "google"
    campaign_medium = "cpc"
    campaign_name = "promo code"
    campaign_term = "testing"
    campaign_content = "This is a testing campaign!"


class ATSSourceCodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.ATSSourceCode'

    name = "Test Name"
    value = "Test Value"
    group = factory.SubFactory(GroupFactory)
    ats_name = "Matt's Jumbo ATS House of Horrors"


class ViewSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.ViewSource'

    name = "Test View Source"
    view_source = "27"


class SpecialCommitmentFactory(factory.django.DjangoModelFactory):
    """
    Create a test SpecialCommit Object. Must be assigned to a site object.
    """
    class Meta:
        model = 'seo.SpecialCommitment'

    name = "Test Special Commitment"
    commit = "TestCommit"


class SeoSiteFactory(SiteFactory):
    class Meta:
        model = 'seo.SeoSite'

    group = factory.SubFactory(GroupFactory)
    site_heading = "This is the site header."
    domain = 'buckconsultants.jobs'
    name = u'buckconsultants.jobs'
    site_title = "Test Site"


class SeoSiteCopyToFactory(SiteFactory):
    class Meta:
        model = 'seo.SeoSite'
        database = copy_to_database

    group = factory.SubFactory(GroupCopyToFactory)
    site_heading = "This is the site header."
    domain = 'qccopiertest.jobs'
    name = u'qccopiertest.jobs'
    site_title = "QC Copier Test Site"


class CustomFacetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.CustomFacet'

    group = factory.SubFactory(GroupFactory)
    name = "Test CustomFacet"
    name_slug = factory.LazyAttribute(lambda x: slugify(x.name))
    querystring = None
    city = ""
    state = ""
    country = ""
    title = ""
    show_production = False


class SeoSiteFacetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.SeoSiteFacet'

    customfacet = factory.SubFactory(CustomFacetFactory)
    seosite = factory.SubFactory(SeoSiteFactory)
    facet_type = SeoSiteFacet.STANDARD


class SeoSiteRedirectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.SeoSiteRedirect'

    redirect_url = 'www.buckconsultants.jobs'
    seosite = factory.SubFactory(SeoSiteFactory)


class ConfigurationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.Configuration'

    backgroundColor = ""
    browse_city_order = 2
    browse_city_show = True
    browse_city_text = ""
    browse_country_order = 4
    browse_country_show = True
    browse_country_text = ""
    browse_facet_order = 6
    browse_facet_show = True
    browse_facet_text = "Facets"
    browse_moc_show = True
    browse_state_order = 3
    browse_state_show = True
    browse_state_text = ""
    browse_title_order = 1
    browse_title_show = False
    browse_title_text = ""
    defaultBlurb = ""
    defaultBlurbTitle = "Test Blurb"
    directemployers_link = "http://directemployers.org"
    facet_tag = "new-jobs"
    fontColor = "666666"
    footer = ""
    group = factory.SubFactory(GroupFactory)
    header = ""
    home_page_template = 'home_page/home_page_billboard.html'
    location_tag = ""
    meta = ""
    num_filter_items_to_show = 10
    num_job_items_to_show = 20
    num_subnav_items_to_show = 5
    primaryColor = "990000"
    status = 1
    title = "Default"
    title_tag = ""
    wide_footer = ""
    wide_header = ""
    percent_featured = 0.5


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.Company'

    id = factory.sequence(lambda n: n+1)
    name = factory.Sequence(lambda n: "Acme Incorporated %d" % n)
    member = True
    company_slug = factory.LazyAttribute(lambda x: slugify(x.name))


class GoogleAnalyticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.GoogleAnalytics'

    web_property_id = "1234"


class BillboardImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.BillboardImage'

    title = "Test Image"
    image_url = "http://fakecdn.jobs/img/test.jpg"
    copyright_info = "test image. I don't really exist."
    source_url = "fakecdn.jobs"
    logo_url = "http://fakecdn.jobs/img.jpg"
    sponsor_url = "fakecdn.jobs"


class CompanyUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.CompanyUser'

    user = factory.SubFactory(UserFactory)
    company = factory.SubFactory(CompanyFactory)

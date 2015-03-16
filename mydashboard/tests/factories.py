import factory
from slugify import slugify

from myjobs.tests.factories import UserFactory
from seo.tests.factories import CompanyFactory


class BusinessUnitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.BusinessUnit'

    id = 1
    title = 'Test Company'
    title_slug = factory.LazyAttribute(lambda x: slugify(x.title))
    federal_contractor = True
    date_updated = "2010-10-18 10:59:24"
    associated_jobs = 4
    date_crawled = "2010-10-18 07:00:02"
    enable_markdown = True

class SeoSiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.SeoSite'

    id = 2
    domain = 'test.jobs'
    name = 'Test Jobs'


class CompanyUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'seo.CompanyUser'

    user = factory.SubFactory(UserFactory)
    company = factory.SubFactory(CompanyFactory)

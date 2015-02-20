import factory

from mydashboard.tests.factories import CompanyFactory
from mypartners.tests.factories import PartnerFactory
from myjobs.tests.factories import UserFactory


class SavedSearchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'mysearches.SavedSearch'

    user = factory.SubFactory(UserFactory)

    url = "http://www.my.jobs/jobs"
    label = "All Jobs"
    feed = "http://www.my.jobs/jobs/feed/rss?"
    is_active = True
    email = "alice@example.com"
    frequency = "W"
    day_of_week = "1"
    jobs_per_email = 5
    notes = "All jobs from www.my.jobs"
    sort_by = "Relevance"


class SavedSearchDigestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'mysearches.SavedSearchDigest'

    user = factory.SubFactory(UserFactory)
    email = "alice@example.com"
    is_active = "True"
    frequency = "D"


class PartnerSavedSearchFactory(SavedSearchFactory):
    class Meta:
        model = 'mysearches.PartnerSavedSearch'

    created_by = factory.SubFactory(UserFactory)
    provider = factory.SubFactory(CompanyFactory)
    partner = factory.SubFactory(PartnerFactory)
    url_extras = ""
    partner_message = ""

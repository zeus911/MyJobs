import datetime
import factory

from mydashboard.tests.factories import CompanyFactory
from postajob.models import Job


class JobFactory(factory.Factory):
    FACTORY_FOR = Job

    title = 'Job Title'
    owner = factory.SubFactory(CompanyFactory)
    reqid = 1
    description = 'The job description.'
    apply_link = 'www.google.com'
    city = 'Indianapolis'
    state = 'Indiana'
    state_short = 'IN'
    country = 'United States of America'
    country_short = 'USA'
    zipcode = 46268
    date_new = factory.LazyAttribute(lambda n: datetime.datetime.now())
    date_updated = factory.LazyAttribute(lambda n: datetime.datetime.now())
    date_expired = factory.LazyAttribute(lambda n: datetime.date.today())
    guid = 'abcdef123456'
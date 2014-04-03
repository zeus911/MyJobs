import factory

from myjobs.tests.factories import UserFactory
from mydashboard.models import (BusinessUnit, Company, CompanyUser,
    SeoSite)


class BusinessUnitFactory(factory.Factory):
    FACTORY_FOR = BusinessUnit

    id = 1
    title = 'Test Company'


class CompanyFactory(factory.Factory):
    FACTORY_FOR = Company

    id = 1
    name = 'Test Company'


class SeoSiteFactory(factory.Factory):
    FACTORY_FOR = SeoSite

    id = 2
    domain = 'http://test.jobs/'
    name = 'Test Jobs'


class CompanyUserFactory(factory.Factory):
    FACTORY_FOR = CompanyUser

    user = factory.SubFactory(UserFactory)
    company = factory.SubFactory(CompanyFactory)

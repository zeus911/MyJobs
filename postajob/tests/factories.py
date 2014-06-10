import datetime
import factory

from mydashboard.tests.factories import CompanyFactory
from postajob.models import (Job, Product, ProductGrouping, PurchasedProduct,
                             SitePackage)


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


# Because of the way the SubFactory works, each Factory was generating
# it's own version of CompanyFactory, causing IntegrityErrors with the pk
# and matching errors between owners on objects that should share owners.
# It ended up being a lot easier just to create a custom "factory"
# for the models that were having this problem instead.

def create_instance(model, data, kwargs):
    if kwargs:
        data.update(kwargs)
    return model.objects.create(**data)


def sitepackage_factory(company, **kwargs):
    sitepackage_data = {
        'owner': company,
        'name': 'Test SitePackage',
    }
    return create_instance(SitePackage, sitepackage_data, kwargs)


def product_factory(package, company, **kwargs):
    product_data = {
        'package': package,
        'owner': company,
        'name': 'Test Product',
        'cost': '5',
        'posting_window_length': 30,
        'max_job_length': 30,
        'num_jobs_allowed': 5,
        'description': 'Test product description.'
    }
    return create_instance(Product, product_data, kwargs)


def productgrouping_factory(company, **kwargs):
    productgrouping_data = {
        'display_order': 100,
        'display_title': 'Test ProductGrouping',
        'explanation': 'Test explanation.',
        'name': 'Test ProductGrouping',
        'owner': company,
    }
    return create_instance(ProductGrouping, productgrouping_data, kwargs)


def purchasedproduct_factory(product, company, **kwargs):
    purchasedproduct_data = {
        'owner': company,
        'product': product,
    }
    return create_instance(PurchasedProduct, purchasedproduct_data, kwargs)
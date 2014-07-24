import datetime

from postajob.models import (Job, JobLocation, Invoice, OfflinePurchase,
                             OfflineProduct, Product, ProductGrouping,
                             PurchasedJob, PurchasedProduct, SitePackage)


# Because of the way the SubFactory works, each Factory was generating
# it's own version of CompanyFactory, causing IntegrityErrors with the pk
# and matching errors between owners on objects that should share owners.
# It ended up being a lot easier just to create a custom "factory"
# for the models that were having this problem instead.
def create_instance(model, data, kwargs):
    if kwargs:
        data.update(kwargs)
    return model.objects.create(**data)


def joblocation_factory(**kwargs):
    joblocation_data = {
        'city': 'Indianapolis',
        'state': 'Indiana',
        'state_short': 'IN',
        'country': 'United States of America',
        'country_short': 'USA',
        'zipcode': '46268',
    }
    return create_instance(JobLocation, joblocation_data, kwargs)


def job_factory(company, user, **kwargs):
    job_data = {
        'title': 'title',
        'owner': company,
        'reqid': '1',
        'description': 'sadfljasdfljasdflasdfj',
        'apply_link': 'www.google.com',
        'date_new': datetime.datetime.now(),
        'date_updated': datetime.datetime.now(),
        'date_expired': datetime.date.today(),
        'created_by': user,
    }
    return create_instance(Job, job_data, kwargs)


def purchasedjob_factory(company, user, purchased_product, **kwargs):
    purchasedjob_data = {
        'title': 'title',
        'owner': company,
        'reqid': '1',
        'description': 'sadfljasdfljasdflasdfj',
        'apply_link': 'www.google.com',
        'city': 'Indianapolis',
        'state': 'Indiana',
        'state_short': 'IN',
        'country': 'United States of America',
        'country_short': 'USA',
        'zipcode': '46268',
        'date_new': datetime.datetime.now(),
        'date_updated': datetime.datetime.now(),
        'date_expired': datetime.date.today(),
        'created_by': user,
        'max_expired_date': datetime.date.today() + datetime.timedelta(days=1),
        'purchased_product': purchased_product,
    }
    return create_instance(PurchasedJob, purchasedjob_data, kwargs)


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
        'invoice': invoice_factory(product.owner),
        'owner': company,
        'product': product,
        'purchase_date': datetime.datetime.now(),
    }
    return create_instance(PurchasedProduct, purchasedproduct_data, kwargs)


def invoice_factory(owner, **kwargs):
    invoice_data = {
        'address_line_one': '123 Street Rd',
        'address_line_two': 'Suite 321',
        'card_exp_date': datetime.date.today(),
        'card_last_four': '1234',
        'city': 'Indianapolis',
        'country': 'US',
        'first_name': 'John',
        'last_name': 'Smith',
        'owner': owner,
        'state': 'Indiana',
        'transaction': '123456',
        'zipcode': '46268',
    }
    return create_instance(Invoice, invoice_data, kwargs)


def offlinepurchase_factory(owner, creator, **kwargs):
    offlinepurchase_data = {
        'created_by': creator,
        'invoice': invoice_factory(owner, transaction='1'),
        'owner': owner,
    }
    return create_instance(OfflinePurchase, offlinepurchase_data, kwargs)


def offlineproduct_factory(product, purchase, **kwargs):
    offlineproduct_data = {
        'offline_purchase': purchase,
        'product': product,
        'product_quantity': 1,
    }
    return create_instance(OfflineProduct, offlineproduct_data, kwargs)
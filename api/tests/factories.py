import factory
from api.models import APIUser


class APIUserFactory(factory.Factory):
    FACTORY_FOR = APIUser

    company = 'Example'
    scope = 1
    view_source = 1
    key = '1'
    jv_api_access = 1
    onet_access = 1
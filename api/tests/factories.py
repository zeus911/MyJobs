from factory import django, fuzzy


class APIUserFactory(django.DjangoModelFactory):
    class Meta:
        model = 'api.APIUser'

    company = 'Example'
    scope = 1
    view_source = 1
    key = fuzzy.FuzzyText(length=5)
    jv_api_access = 1
    onet_access = 1
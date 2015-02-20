import factory
import factory.fuzzy
import factory.django

from django.contrib.contenttypes.models import ContentType

from slugify import slugify
from seo.models import BusinessUnit


class OnetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'moc_coding.Onet'

    title = "Some Onet"
    code = "99999999"


class MocDetailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'moc_coding.MocDetail'

    primary_value = "01"
    service_branch = "c"
    military_description = "General Command and Staff"
    civilian_description = "Business General"


class MocFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'moc_coding.Moc'

    code = factory.fuzzy.FuzzyText('01')
    branch = 'coast-guard'
    title = "General Command and Staff"
    title_slug = factory.LazyAttribute(lambda x: slugify(x.title))
    moc_detail = factory.SubFactory(MocDetailFactory)


class CustomCareerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'moc_coding.CustomCareer'

    moc = factory.SubFactory(MocFactory)
    onet_id = "99999999"
    content_type_id = factory.LazyAttribute(
        lambda x: ContentType.objects.get_for_model(BusinessUnit).pk)

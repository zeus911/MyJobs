import factory
import factory.django

from django.contrib.contenttypes.models import ContentType

from slugify import slugify
from moc_coding.models import CustomCareer, Moc, MocDetail, Onet
from seo.models import BusinessUnit


class OnetFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Onet

    title = "Some Onet"
    code = "99999999"


class MocFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Moc
    id = 1 
    code = "01"
    branch = "coast-guard"
    title = "General Command and Staff"
    title_slug = factory.LazyAttribute(lambda x: slugify(x.title))
    moc_detail_id = factory.SubFactory(MocDetailFactory)


class MocDetailFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = MocDetail

    id = 1
    primary_value = "01"
    service_branch = "c"
    military_description = "General Command and Staff"
    civilian_description = "Business General"


class CustomCareerFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = CustomCareer

    moc_id = 1
    onet_id = "99999999"
    content_type_id = factory.LazyAttribute(lambda x: ContentType.objects.get_for_model(BusinessUnit).pk)
    object_id = 1
    

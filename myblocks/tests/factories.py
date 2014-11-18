from factory import django, SubFactory

from myblocks import models
from seo.tests.factories import SeoSiteFactory


class BlockFactory(django.DjangoModelFactory):
    FACTORY_FOR = models.Block

    name = 'Test Block'
    offset = 0
    span = 6


class ContentBlockFactory(BlockFactory):
    FACTORY_FOR = models.ContentBlock


class ImageBlockFactory(BlockFactory):
    FACTORY_FOR = models.ImageBlock

    image_url = 'https://www.my.jobs'


class LoginBlockFactory(BlockFactory):
    FACTORY_FOR = models.LoginBlock


class RegistrationBlockFactory(BlockFactory):
    FACTORY_FOR = models.RegistrationBlock


class ColumnBlockFactory(BlockFactory):
    FACTORY_FOR = models.ColumnBlock


class RowFactory(django.DjangoModelFactory):
    FACTORY_FOR = models.Row


class PageFactory(django.DjangoModelFactory):
    FACTORY_FOR = models.Page

    page_type = 'login'
    site = SubFactory(SeoSiteFactory)

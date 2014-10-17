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

    content = 'Test content.'


class ImageBlockFactory(BlockFactory):
    FACTORY_FOR = models.ImageBlock

    image_url = 'https://www.my.jobs'


class LoginBlockFactory(BlockFactory):
    FACTORY_FOR = models.LoginBlock


class RegistrationBlockFactory(BlockFactory):
    FACTORY_FOR = models.RegistrationBlock


class VerticalMultiBlockFactory(BlockFactory):
    FACTORY_FOR = models.VerticalMultiBlock


class ColumnFactory(django.DjangoModelFactory):
    FACTORY_FOR = models.Column


class PageFactory(django.DjangoModelFactory):
    FACTORY_FOR = models.Page

    bootstrap_version = 1
    page_type = 'login'
    site = SubFactory(SeoSiteFactory)

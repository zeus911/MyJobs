from factory import django, SubFactory

from seo.tests.factories import SeoSiteFactory


class BlockFactory(django.DjangoModelFactory):
    class Meta:
        model = 'myblocks.Block'

    name = 'Test Block'
    offset = 0
    span = 6


class ContentBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.ContentBlock'


class ImageBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.ImageBlock'

    image_url = 'https://www.my.jobs'


class LoginBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.LoginBlock'


class RegistrationBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.RegistrationBlock'


class ColumnBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.ColumnsBlock'


class RowFactory(django.DjangoModelFactory):
    class Meta:
        model = 'myblocks.Row'


class PageFactory(django.DjangoModelFactory):
    class Meta:
        model = 'myblocks.Page'

    page_type = 'login'
    site = SubFactory(SeoSiteFactory)

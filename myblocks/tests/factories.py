from factory import django, post_generation


class BlockFactory(django.DjangoModelFactory):
    class Meta:
        model = 'myblocks.Block'

    name = 'Test Block'
    offset = 0
    span = 6


class ApplyLinkBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.ApplyLinkBlock'


class BreadboxBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.BreadboxBlock'


class ContentBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.ContentBlock'


class FacetBlurbBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.FacetBlurbBlock'


class JobDetailBlockFacetory(BlockFactory):
    class Meta:
        model = 'myblocks.JobDetailBlock'


class JobDetailBreadboxBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.JobDetailBreadboxBlock'


class JobDetailHeaderBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.JobDetailHeaderBlock'


class LoginBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.LoginBlock'


class MoreButtonBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.MoreButtonBlock'


class RegistrationBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.RegistrationBlock'


class SavedSearchWidgetBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.SavedSearchWidgetBlock'


class SearchBoxBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.SearchBoxBlock'


class SearchFilterBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.SearchFilterBlock'


class SearchResultFactory(BlockFactory):
    class Meta:
        model = 'myblocks.SearchResultBlock'


class SearchResultHeaderFactory(BlockFactory):
    class Meta:
        model = 'myblocks.SearchResultHeaderBlock'


class ShareBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.ShareBlock'


class VeteranSearchBoxBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.VeteranSearchBox'


class ColumnBlockFactory(BlockFactory):
    class Meta:
        model = 'myblocks.ColumnBlock'


class RowFactory(django.DjangoModelFactory):
    class Meta:
        model = 'myblocks.Row'


class PageFactory(django.DjangoModelFactory):
    class Meta:
        model = 'myblocks.Page'

    page_type = 'login'

    @post_generation
    def sites(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for site in extracted:
                self.sites.add(site)

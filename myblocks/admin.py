from django.contrib import admin

from myblocks import forms, models


class ColumnBlockOrderInline(admin.TabularInline):
    model = models.ColumnBlockOrder
    fk_name = 'column_block'
    save_as = True


class BlockAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'offset', 'span')
    save_as = True


class ColumnBlockAdmin(BlockAdmin):
    form = forms.ColumnBlockForm
    inlines = (ColumnBlockOrderInline, )


class ApplyLinkBlockAdmin(BlockAdmin):
    form = forms.ApplyLinkBlockForm


class BreadboxBlockAdmin(BlockAdmin):
    form = forms.BreadboxBlockForm


class ContentBlockAdmin(BlockAdmin):
    form = forms.ContentBlockForm


class FacetBlurbBlockAdmin(BlockAdmin):
    form = forms.FacetBlurbBlockForm


class JobDetailBlockAdmin(BlockAdmin):
    form = forms.JobDetailBlockForm


class JobDetailBreadboxBlockAdmin(BlockAdmin):
    form = forms.JobDetailBreadboxBlockForm


class JobDetailHeaderBlockAdmin(BlockAdmin):
    form = forms.JobDetailHeaderBlockForm


class LoginBlockAdmin(BlockAdmin):
    form = forms.LoginBlockForm


class MoreButtonBlockAdmin(BlockAdmin):
    form = forms.MoreButtonBlockForm


class RegistrationBlockAdmin(BlockAdmin):
    form = forms.RegistrationBlockForm


class SavedSearchWidgetBlockAdmin(BlockAdmin):
    form = forms.SavedSearchWidgetBlockForm


class SearchBoxBlockAdmin(BlockAdmin):
    form = forms.SearchBoxBlockForm


class SearchFilterBlockAdmin(BlockAdmin):
    form = forms.SearchFilterBlockForm


class VeteranSearchBoxAdmin(BlockAdmin):
    form = forms.VeteranSearchBoxForm


class SearchResultBlockAdmin(BlockAdmin):
    form = forms.SearchResultBlockForm


class SearchResultHeaderBlockAdmin(BlockAdmin):
    form = forms.SearchResultHeaderBlockForm


class ShareBlockAdmin(BlockAdmin):
    form = forms.ShareBlockForm


class BlockOrderInline(admin.TabularInline):
    model = models.Row.blocks.through
    save_as = True


class RowOrderInline(admin.TabularInline):
    model = models.Page.rows.through
    save_as = True


class PageAdmin(admin.ModelAdmin):
    form = forms.PageForm
    inlines = (RowOrderInline, )
    list_display = ('name', 'human_readable_page_type',
                    'human_readable_sites', 'human_readable_status')
    list_filter = ('sites__domain', )
    save_as = True
    search_fields = ('name', 'sites__domain', )


class RowAdmin(admin.ModelAdmin):
    form = forms.RowForm
    inlines = (BlockOrderInline, )
    save_as = True


admin.site.register(models.ApplyLinkBlock, ApplyLinkBlockAdmin)
admin.site.register(models.BreadboxBlock, BreadboxBlockAdmin)
admin.site.register(models.ContentBlock, ContentBlockAdmin)
admin.site.register(models.FacetBlurbBlock, FacetBlurbBlockAdmin)
admin.site.register(models.LoginBlock, LoginBlockAdmin)
admin.site.register(models.JobDetailBlock, JobDetailBlockAdmin)
admin.site.register(models.JobDetailBreadboxBlock, JobDetailBreadboxBlockAdmin)
admin.site.register(models.JobDetailHeaderBlock, JobDetailHeaderBlockAdmin)
admin.site.register(models.MoreButtonBlock, MoreButtonBlockAdmin)
admin.site.register(models.SavedSearchWidgetBlock, SavedSearchWidgetBlockAdmin)
admin.site.register(models.SearchBoxBlock, SearchBoxBlockAdmin)
admin.site.register(models.SearchFilterBlock, SearchFilterBlockAdmin)
admin.site.register(models.VeteranSearchBox, VeteranSearchBoxAdmin)
admin.site.register(models.SearchResultBlock, SearchResultBlockAdmin)
admin.site.register(models.SearchResultHeaderBlock, SearchResultHeaderBlockAdmin)
admin.site.register(models.ShareBlock, ShareBlockAdmin)
admin.site.register(models.RegistrationBlock, RegistrationBlockAdmin)
admin.site.register(models.ColumnBlock, ColumnBlockAdmin)

admin.site.register(models.Row, RowAdmin)
admin.site.register(models.Page, PageAdmin)
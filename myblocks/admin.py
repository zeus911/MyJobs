from django.contrib import admin

from myblocks import forms, models


class ColumnBlockOrderInline(admin.TabularInline):
    model = models.ColumnBlockOrder
    fk_name = 'column_block'
    save_as = True


class ColumnBlockAdmin(admin.ModelAdmin):
    form = forms.ColumnBlockForm
    inlines = (ColumnBlockOrderInline, )
    save_as = True


class ApplyLinkBlockAdmin(admin.ModelAdmin):
    form = forms.ApplyLinkBlockForm
    save_as = True


class BreadboxBlockAdmin(admin.ModelAdmin):
    form = forms.BreadboxBlockForm
    save_as = True


class ContentBlockAdmin(admin.ModelAdmin):
    form = forms.ContentBlockForm
    save_as = True


class FacetBlurbBlockAdmin(admin.ModelAdmin):
    form = forms.FacetBlurbBlockForm
    save_as = True


class JobDetailBlockAdmin(admin.ModelAdmin):
    form = forms.JobDetailBlockForm
    save_as = True


class JobDetailBreadboxBlockAdmin(admin.ModelAdmin):
    form = forms.JobDetailBreadboxBlockForm
    save_as = True


class JobDetailHeaderBlockAdmin(admin.ModelAdmin):
    form = forms.JobDetailHeaderBlockForm
    save_as = True


class LoginBlockAdmin(admin.ModelAdmin):
    form = forms.LoginBlockForm
    save_as = True


class MoreButtonBlockAdmin(admin.ModelAdmin):
    form = forms.MoreButtonBlockForm
    save_as = True


class RegistrationBlockAdmin(admin.ModelAdmin):
    form = forms.RegistrationBlockForm
    save_as = True


class SavedSearchWidgetBlockAdmin(admin.ModelAdmin):
    form = forms.SavedSearchWidgetBlockForm
    save_as = True


class SearchBoxBlockAdmin(admin.ModelAdmin):
    form = forms.SearchBoxBlockForm
    save_as = True


class SearchFilterBlockAdmin(admin.ModelAdmin):
    form = forms.SearchFilterBlockForm
    save_as = True


class VeteranSearchBoxAdmin(admin.ModelAdmin):
    form = forms.VeteranSearchBoxForm
    save_as = True


class SearchResultBlockAdmin(admin.ModelAdmin):
    form = forms.SearchResultBlockForm
    save_as = True


class SearchResultHeaderBlockAdmin(admin.ModelAdmin):
    form = forms.SearchResultHeaderBlockForm
    save_as = True


class ShareBlockAdmin(admin.ModelAdmin):
    form = forms.ShareBlockForm
    save_as = True


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
                    'human_readable_sites', )
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
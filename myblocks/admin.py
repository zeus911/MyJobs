from django.contrib import admin

from myblocks import forms, models


class ColumnBlockOrderInline(admin.TabularInline):
    model = models.ColumnBlockOrder
    fk_name = 'column_block'


class ColumnBlockAdmin(admin.ModelAdmin):
    form = forms.ColumnBlockForm
    inlines = (ColumnBlockOrderInline, )


class ContentBlockAdmin(admin.ModelAdmin):
    form = forms.ContentBlockForm


class ImageBlockAdmin(admin.ModelAdmin):
    form = forms.ImageBlockForm


class LoginBlockAdmin(admin.ModelAdmin):
    form = forms.LoginBlockForm


class RegistrationBlockAdmin(admin.ModelAdmin):
    form = forms.RegistrationBlockForm


class SavedSearchWidgetBlockAdmin(admin.ModelAdmin):
    form = forms.SavedSearchWidgetBlockForm


class SearchBoxBlockAdmin(admin.ModelAdmin):
    form = forms.SearchBoxBlockForm


class SearchFilterBlockAdmin(admin.ModelAdmin):
    form = forms.SearchFilterBlockForm


class VeteranSearchBoxAdmin(admin.ModelAdmin):
    form = forms.VeteranSearchBoxForm


class SearchResultBlockAdmin(admin.ModelAdmin):
    form = forms.SearchResultBlockForm


class ShareBlockAdmin(admin.ModelAdmin):
    form = forms.ShareBlockForm


class BlockOrderInline(admin.TabularInline):
    model = models.Row.blocks.through


class RowOrderInline(admin.TabularInline):
    model = models.Page.rows.through


class PageAdmin(admin.ModelAdmin):
    inlines = (RowOrderInline, )


class RowAdmin(admin.ModelAdmin):
    form = forms.RowForm
    inlines = (BlockOrderInline, )


admin.site.register(models.ContentBlock, ContentBlockAdmin)
admin.site.register(models.ImageBlock, ImageBlockAdmin)
admin.site.register(models.LoginBlock, LoginBlockAdmin)
admin.site.register(models.RegistrationBlock, RegistrationBlockAdmin)
admin.site.register(models.ColumnBlock, ColumnBlockAdmin)

admin.site.register(models.Row, RowAdmin)
admin.site.register(models.Page, PageAdmin)
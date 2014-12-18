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


class ContentBlockAdmin(admin.ModelAdmin):
    form = forms.ContentBlockForm
    save_as = True


class ImageBlockAdmin(admin.ModelAdmin):
    form = forms.ImageBlockForm
    save_as = True


class LoginBlockAdmin(admin.ModelAdmin):
    form = forms.LoginBlockForm
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
    inlines = (RowOrderInline, )
    save_as = True


class RowAdmin(admin.ModelAdmin):
    form = forms.RowForm
    inlines = (BlockOrderInline, )
    save_as = True


admin.site.register(models.ContentBlock, ContentBlockAdmin)
admin.site.register(models.ImageBlock, ImageBlockAdmin)
admin.site.register(models.LoginBlock, LoginBlockAdmin)
admin.site.register(models.RegistrationBlock, RegistrationBlockAdmin)
admin.site.register(models.ColumnBlock, ColumnBlockAdmin)

admin.site.register(models.Row, RowAdmin)
admin.site.register(models.Page, PageAdmin)
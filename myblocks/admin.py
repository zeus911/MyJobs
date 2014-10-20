from django.contrib import admin

from myblocks import models


class BlockOrderIndline(admin.TabularInline):
    model = models.Row.blocks.through


class RowAdmin(admin.ModelAdmin):
    inlines = (BlockOrderIndline, )


class RowOrderInline(admin.TabularInline):
    model = models.Page.rows.through


class PageAdmin(admin.ModelAdmin):
    inlines = (RowOrderInline, )


admin.site.register(models.ContentBlock)
admin.site.register(models.ImageBlock)
admin.site.register(models.LoginBlock)
admin.site.register(models.RegistrationBlock)
admin.site.register(models.ColumnBlock)

admin.site.register(models.Row, RowAdmin)
admin.site.register(models.Page, PageAdmin)
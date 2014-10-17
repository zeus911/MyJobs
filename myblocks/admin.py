from django.contrib import admin

from myblocks import models

admin.site.register(models.Block)
admin.site.register(models.ContentBlock)
admin.site.register(models.ImageBlock)
admin.site.register(models.LoginBlock)
admin.site.register(models.RegistrationBlock)
admin.site.register(models.VerticalMultiBlock)

admin.site.register(models.Column)
admin.site.register(models.Page)

admin.site.register(models.BlockOrder)
admin.site.register(models.ColumnOrder)
admin.site.register(models.VerticalMultiBlockOrder)

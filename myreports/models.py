from django.db import models


class Report(models.Model):
    created_by = models.ForeignKey('myjobs.User')
    owner = models.ForeignKey('seo.Company')
    created_on = models.DateTimeField(auto_now_add=True)
    # path used to generate the report; identifies the app and model queried on
    path = models.CharField(max_length=255)
    # json encoded string of the params used to filter
    params = models.CharField(max_length=255)
    results = models.FileField(upload_to='reports')

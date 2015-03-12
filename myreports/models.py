import json
from django.db import models


class Report(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey('myjobs.User')
    owner = models.ForeignKey('seo.Company')
    created_on = models.DateTimeField(auto_now_add=True)
    # path used to generate the report; identifies the app and model queried on
    path = models.CharField(max_length=255)
    # json encoded string of the params used to filter
    params = models.CharField(max_length=255)
    results = models.FileField(upload_to='reports')

    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        self._results = self.results.read()

    @property
    def json(self):
        return self._results

    @property
    def python(self):
        return json.loads(self._results)

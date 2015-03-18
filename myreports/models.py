import json
from django.db import models
from django.db.models.loading import get_model


class Report(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey('myjobs.User')
    owner = models.ForeignKey('seo.Company')
    created_on = models.DateTimeField(auto_now_add=True)
    app = models.CharField(default='mypartners', max_length=50)
    model = models.CharField(default='contactrecord', max_length=50)
    # json encoded string of the params used to filter
    params = models.TextField()
    results = models.FileField(upload_to='reports')

    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        if self.results:
            self._results = self.results.read()
        else:
            self._results = '{}'

    @property
    def json(self):
        return self._results

    @property
    def python(self):
        return json.loads(self._results)

    @property
    def queryset(self):
        pks = [record['pk'] for record in self.python]
        return get_model(self.app, self.model).objects.filter(pk__in=pks)

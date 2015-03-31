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
    # included columns and sort order
    values = models.CharField(null=True, max_length=500)
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
        q = models.Q()
        for record in self.python:
            q |= models.Q(**record)

        queryset = get_model(self.app, self.model).objects.filter(q)

        return queryset

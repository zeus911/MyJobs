import json
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.loading import get_model

from myreports.helpers import serialize


class Report(models.Model):
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey('myjobs.User')
    owner = models.ForeignKey('seo.Company')
    created_on = models.DateTimeField(auto_now_add=True)
    order_by = models.CharField(max_length=50, blank=True, null=True)
    app = models.CharField(default='mypartners', max_length=50)
    model = models.CharField(default='contactrecord', max_length=50)
    # included columns and sort order
    values = models.CharField(max_length=500, default='[]')
    # json encoded string of the params used to filter
    params = models.TextField()
    results = models.FileField(upload_to='reports')

    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)
        if self.results:
            try:
                self._results = self.results.read()
            except IOError:
                values = json.loads(self.values)
                contents = serialize('json', self.queryset, values=values)
                results = ContentFile(contents)

                self.results.save('%s-%s.json' % (self.name, self.pk), results)
                self._results = contents
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
        model = get_model(self.app, self.model)
        params = json.loads(self.params)
        return model.objects.from_search(self.owner, params)

    def __unicode__(self):
        return self.name

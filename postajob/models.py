from datetime import datetime
from uuid import uuid4

from django.db import models

from mydashboard.models import Company, SeoSite


class Job(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    uid = models.CharField(max_length=255, unique=True)

    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company)
    reqid = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    show_on_sites = models.ManyToManyField(SeoSite, blank=True, null=True)
    is_syndicated = models.BooleanField(default=False)

    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=200, blank=True)
    state_short = models.CharField(max_length=3, blank=True)
    country = models.CharField(max_length=200, blank=True)
    country_short = models.CharField(max_length=3, blank=True)
    zipcode = models.CharField(max_length=15, blank=True)

    date_new = models.DateTimeField()
    date_updated = models.DateTimeField()

    def __unicode__(self):
        return '{company} - {title}'.format(company=self.company.name,
                                            title=self.title)

    def add_to_solr(self):
        pass

    def get_apply_link(self):
        return 'http://my.jobs/{uid}'.format(guid=self.uid)

    def generate_uid(self):
        if not self.uid:
            uid = uuid4().hex
            if Job.objects.filter(uid=uid):
                self.generate_uid()
            else:
                self.uid = uid

    def save(self, **kwargs):
        if not self.pk:
            self.date_new = datetime.now()
        self.date_updated = datetime.now()
        self.generate_uid()
        super(Job, self).save(**kwargs)
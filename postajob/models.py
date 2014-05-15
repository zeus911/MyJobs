import json
from datetime import datetime
from urllib import urlencode
from urllib2 import Request, urlopen
from uuid import uuid4

from django.conf import settings
from django.db import models

from mydashboard.models import BusinessUnit, Company, SeoSite


class Job(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    guid = models.CharField(max_length=255, unique=True)
    buid = models.ForeignKey(BusinessUnit)

    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company)
    reqid = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    apply_link = models.URLField()
    show_on_sites = models.ManyToManyField(SeoSite, blank=True, null=True)
    is_syndicated = models.BooleanField(default=False)

    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=200, blank=True)
    state_short = models.CharField(max_length=3, blank=True)
    country = models.CharField(max_length=200, blank=True)
    country_short = models.CharField(max_length=3, blank=True)
    zipcode = models.CharField(max_length=15, blank=True)

    date_new = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{company} - {title}'.format(company=self.company.name,
                                            title=self.title)

    def add_to_solr(self):
        """
        Microsites is expecting following fields: id (postajob.job.id),
        buid, city, company (company.id), country, country_short, date_new,
        date_updated, description, guid, link, on_sites, state,
        state_short, reqid, title, uid, and zipcode.
        """
        on_sites = ",".join([str(x.id) for x in self.show_on_sites.all()])
        job = {
            'id': self.id,
            'buid': '',
            'city': self.city,
            'company': self.company.id,
            'country': self.country,
            'country_short': self.country_short,
            # Microsites expects date format '%Y-%m-%d %H:%M:%S.%f'
            'date_new': str(self.date_new.replace(tzinfo=None)),
            'date_updated': str(self.date_updated.replace(tzinfo=None)),
            'description': self.description,
            'guid': self.guid,
            'link': self.apply_link,
            'on_sites': on_sites,
            'state': self.state,
            'state_short': self.state_short,
            'reqid': self.reqid,
            'title': self.title,
            'uid': self.id,
            'zipcode': self.zipcode
        }
        data = urlencode({
            'key': settings.POSTAJOB_API_KEY,
            'jobs': json.dumps([job])
        })
        request = Request(settings.POSTAJOB_URLS['post'], data)
        try:
            response = urlopen(request).read()
        except Exception, e:
            print e

    def delete(self, using=None):
        self.remove_from_solr()
        return super(Job, self).delete(using)

    def remove_from_solr(self):
        data = urlencode({
            'key': settings.POSTAJOB_API_KEY,
            'guids': self.guid
        })
        request = Request(settings.POSTAJOB_URLS['delete'], data)
        response = urlopen(request).read()
        return response

    def generate_guid(self):
        if not self.guid:
            guid = uuid4().hex
            if Job.objects.filter(guid=guid):
                self.generate_guid()
            else:
                self.guid = guid

    @staticmethod
    def get_country_choices():
        country_dict = Job.get_country_map()
        return [(x, x) for x in sorted(country_dict.keys())]

    @staticmethod
    def get_country_map():
        data_url = 'https://d2e48ltfsb5exy.cloudfront.net/myjobs/data/countries.json'
        data_list = json.loads(urlopen(data_url).read())['countries']
        return dict([(x['name'], x['code']) for x in data_list])

    @staticmethod
    def get_state_choices():
        state_dict = Job.get_state_map()
        return [(x, x) for x in sorted(state_dict.keys())]

    @staticmethod
    def get_state_map():
        data_url = 'https://d2e48ltfsb5exy.cloudfront.net/myjobs/data/usa_regions.json'
        data_list = json.loads(urlopen(data_url).read())['regions']
        state_map = dict([(x['name'], x['code']) for x in data_list])
        state_map['None'] = 'None'
        return state_map


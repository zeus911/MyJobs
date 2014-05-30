import datetime
import json
from urllib import urlencode
import urllib2
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete

from mydashboard.models import Company, SeoSite


class Job(models.Model):
    help_text = {
        'apply_email': 'The email address where candidates should send their '
                       'application.',
        'apply_info': 'Describe how dandidates should apply for this job.',
        'apply_link': 'The URL of the application form.',
        'apply_type': 'How should applicants submit their application?',
        'autorenew': 'Automatically renew this job for an additional 30 '
                     'days whenever it expires.',
        'city': 'The city where the job is located.',
        'country': 'The country where the job is located.',
        'date_expired': 'When the job will be automatically removed from '
                        'the site.',
        'description': 'The job description.',
        'is_expired': 'Mark this job as expired to remove it from any site(s). '
                      'This does <b>not</b> delete the job.',
        'reqid': 'The Requisition ID from your system, if any.',
        'state': 'The state where the job is located.',
        'title': 'The title of the job as you want it to appear.',
        'zipcode': 'The zipcode of the job location.',
    }

    id = models.AutoField(primary_key=True, unique=True)
    guid = models.CharField(max_length=255, unique=True)

    title = models.CharField(max_length=255, help_text=help_text['title'])
    company = models.ForeignKey(Company)
    reqid = models.CharField(max_length=50, verbose_name="Requisition ID",
                             help_text=help_text['reqid'], blank=True)
    description = models.TextField(help_text=help_text['description'])
    # This really should be a URLField, but URLFields don't allow for
    # mailto links.
    apply_link = models.TextField(blank=True, verbose_name="Apply Link",
                                  help_text=help_text['apply_link'])
    apply_info = models.TextField(blank=True, verbose_name="Apply Instructions",
                                  help_text=help_text['apply_info'])
    show_on_sites = models.ManyToManyField(SeoSite, null=True)
    is_syndicated = models.BooleanField(default=False,
                                        verbose_name="Syndicated")

    city = models.CharField(max_length=255,
                            help_text=help_text['city'])
    state = models.CharField(max_length=200, verbose_name='State',
                             help_text=help_text['state'])
    state_short = models.CharField(max_length=3)
    country = models.CharField(max_length=200,
                               help_text=help_text['country'])
    country_short = models.CharField(max_length=3)
    zipcode = models.CharField(max_length=15, blank=True,
                               help_text=help_text['zipcode'])

    date_new = models.DateTimeField(auto_now=True)
    date_updated = models.DateTimeField(auto_now_add=True)
    date_expired = models.DateField(help_text=help_text['date_expired'])
    is_expired = models.BooleanField(default=False, verbose_name="Expired",
                                     help_text=help_text['is_expired'])
    autorenew = models.BooleanField(default=False, verbose_name="Auto-Renew",
                                    help_text=help_text['autorenew'])

    def __unicode__(self):
        return '{company} - {title}'.format(company=self.company.name,
                                            title=self.title)

    def add_to_solr(self):
        """
        Microsites is expecting following fields: id (postajob.job.id),
        apply_info, city, company (company.id), country, country_short,
        date_new, date_updated, description, guid, link, on_sites, state,
        state_short, reqid, title, uid, and zipcode.
        """
        if self.show_on_sites.all():
            on_sites = ",".join([str(x.id) for x in self.show_on_sites.all()])
        else:
            on_sites = ''
        job = {
            'id': self.id,
            'city': self.city,
            'company': self.company.id,
            'country': self.country,
            'country_short': self.country_short,
            # Microsites expects date format '%Y-%m-%d %H:%M:%S.%f' or
            # '%Y-%m-%d %H:%M:%S'.
            'date_new': str(self.date_new.replace(tzinfo=None)),
            'date_updated': str(self.date_updated.replace(tzinfo=None)),
            'description': self.description,
            'guid': self.guid,
            'link': self.apply_link,
            'apply_info': self.apply_info,
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
        request = urllib2.Request(settings.POSTAJOB_URLS['post'], data)
        urllib2.urlopen(request).read()

    def save(self, **kwargs):
        self.generate_guid()

        if self.is_expired and self.date_expired > datetime.date.today():
            self.date_expired = datetime.date.today()

        job = super(Job, self).save(**kwargs)

        if not self.is_expired:
            self.add_to_solr()
        else:
            self.remove_from_solr()

        return job

    def remove_from_solr(self):
        data = urlencode({
            'key': settings.POSTAJOB_API_KEY,
            'guids': self.guid
        })
        request = urllib2.Request(settings.POSTAJOB_URLS['delete'], data)
        urllib2.urlopen(request).read()

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
        data_list = json.loads(urllib2.urlopen(data_url).read())['countries']
        return dict([(x['name'], x['code']) for x in data_list])

    @staticmethod
    def get_state_choices():
        state_dict = Job.get_state_map()
        return [(x, x) for x in sorted(state_dict.keys())]

    @staticmethod
    def get_state_map():
        data_url = 'https://d2e48ltfsb5exy.cloudfront.net/myjobs/data/usa_regions.json'
        data_list = json.loads(urllib2.urlopen(data_url).read())['regions']
        state_map = dict([(x['name'], x['code']) for x in data_list])
        state_map['None'] = 'None'
        return state_map


def on_delete(sender, instance, **kwargs):
    instance.remove_from_solr()
pre_delete.connect(on_delete, sender=Job)
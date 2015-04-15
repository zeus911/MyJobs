import hmac
from hashlib import sha1
import uuid

from django.db import models


class APIUser(models.Model):
    class Meta:
        verbose_name = 'API User'

    SCOPE_CHOICES = (('1', 'All'), ('7', 'Network Only'), )

    company = models.CharField(max_length=255, verbose_name="Company")
    key = models.CharField(max_length=255, unique=True)

    first_name = models.CharField(max_length=200, blank=True, default='')
    last_name = models.CharField(max_length=200, blank=True, default='')
    email = models.CharField(max_length=200, blank=True, default='')
    phone = models.CharField(max_length=30,  blank=True, default='')

    scope = models.CharField(max_length=1, choices=SCOPE_CHOICES, default=1)
    jv_api_access = models.BooleanField(default=0,
                                        verbose_name='Job View Access')
    onet_access = models.BooleanField(default=0, verbose_name='Onet Access')

    view_source = models.IntegerField('seo.ViewSource', null=True,
                                      db_column='view_source_id')
    disable = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_disabled = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.company

    def create_key(self):
        self.key = hmac.new(uuid.uuid4().bytes, digestmod=sha1).hexdigest()
        self.save()

    def save(self, *args, **kwargs):
        if not self.key:
            self.create_key()
        return super(APIUser, self).save(*args, **kwargs)


class CityToCentroidMapping(models.Model):
    city = models.CharField(max_length=255, db_index=True)
    state = models.CharField(max_length=3, db_index=True)
    centroid_lat = models.CharField(max_length=25)
    centroid_lon = models.CharField(max_length=25)


class ZipCodeToCentroidMapping(models.Model):
    zip_code = models.CharField(max_length=7, unique=True, db_index=True)
    centroid_lat = models.CharField(max_length=25)
    centroid_lon = models.CharField(max_length=25)


class Search(models.Model):
    query = models.TextField()
    solr_params = models.TextField()
    user = models.ForeignKey('APIUser', db_index=True)
    date_last_accessed = models.DateTimeField(auto_now=True, null=True,
                                              db_index=True)


class Industry(models.Model):
    industry_id = models.IntegerField(max_length=255, primary_key=True)
    industry = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return "%s %s" % (self.industry, self.industry_id)


class Country(models.Model):
    country_code = models.IntegerField(max_length=255, primary_key=True)
    country = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.country

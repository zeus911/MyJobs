from datetime import date, timedelta
import json
import operator
from urllib import urlencode
import urllib2
from uuid import uuid4

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.signals import pre_delete


class BaseModel(models.Model):
    class Meta:
        abstract = True

    def user_has_access(self, user):
        """
        In order for a user to have access they must be a company user
        for the Company that owns the object.
        """
        return user in self.owner.admins.all()


class Job(BaseModel):
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
        'post_to': 'Select either the entire My.jobs network, or one of your '
                   'corporate sites. Posting to the network will make this '
                   'job available to all of your microsites.',
        'reqid': 'The Requisition ID from your system, if any.',
        'state': 'The state where the job is located.',
        'title': 'The title of the job as you want it to appear.',
        'zipcode': 'The zipcode of the job location.',
    }
    guid = models.CharField(max_length=255, unique=True)

    title = models.CharField(max_length=255, help_text=help_text['title'])
    owner = models.ForeignKey('mydashboard.Company')
    reqid = models.CharField(max_length=50, verbose_name="Requisition ID",
                             help_text=help_text['reqid'], blank=True)
    description = models.TextField(help_text=help_text['description'])
    # This really should be a URLField, but URLFields don't allow for
    # mailto links.
    apply_link = models.TextField(blank=True, verbose_name="Apply Link",
                                  help_text=help_text['apply_link'])
    apply_info = models.TextField(blank=True, verbose_name="Apply Instructions",
                                  help_text=help_text['apply_info'])
    site_packages = models.ManyToManyField('SitePackage', null=True)
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
    created_by = models.ForeignKey('myjobs.User')

    def __unicode__(self):
        return '{company} - {title}'.format(company=self.owner.name,
                                            title=self.title)

    def solr_dict(self):
        if self.site_packages.all():
            package_list = self.site_packages.all().values_list('pk', flat=True)
            package_list = list(package_list)
            if (self.site_packages.all().count() == 1 and
                    self.site_packages.all()[0].company_set.all().count() > 0):
                # If it's posted to a company site_pacakge only, that means it
                # was posted to all network + company sites, so add
                # the all sites flag.
                package_list.append(0)
            on_sites = ",".join([str(package) for package in package_list])
        else:
            on_sites = '0'
        job = {
            'id': self.id,
            'city': self.city,
            'company': self.owner.id,
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
        return job

    def add_to_solr(self):
        """
        Microsites is expecting following fields: id (postajob.job.id),
        apply_info, city, company (company.id), country, country_short,
        date_new, date_updated, description, guid, link, on_sites, state,
        state_short, reqid, title, uid, and zipcode.
        """
        job = self.solr_dict()
        data = urlencode({
            'key': settings.POSTAJOB_API_KEY,
            'jobs': json.dumps([job])
        })
        request = urllib2.Request(settings.POSTAJOB_URLS['post'], data)
        urllib2.urlopen(request).read()

    def save(self, **kwargs):
        self.generate_guid()

        if self.is_expired and self.date_expired > date.today():
            self.date_expired = date.today()

        super(Job, self).save(**kwargs)
        if not self.is_expired:
            self.add_to_solr()
        else:
            self.remove_from_solr()

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

    def on_sites(self):
        from mydashboard.models import SeoSite
        return SeoSite.objects.filter(sitepackage__job=self)

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
        state_choices = [(x, x) for x in sorted(state_dict.keys())]
        none_choice = state_choices.pop(state_choices.index(('None', 'None')))
        state_choices.insert(0, none_choice)
        return state_choices

    @staticmethod
    def get_state_map():
        data_url = 'https://d2e48ltfsb5exy.cloudfront.net/myjobs/data/usa_regions.json'
        data_list = json.loads(urllib2.urlopen(data_url).read())['regions']
        state_map = dict([(x['name'], x['code']) for x in data_list])
        state_map['None'] = 'None'
        return state_map


class PurchasedJob(Job):
    max_expired_date = models.DateField(editable=False)
    purchased_product = models.ForeignKey('PurchasedProduct')
    is_approved = models.BooleanField(default=False)

    def save(self, **kwargs):
        super(PurchasedJob, self).save(**kwargs)
        self.site_packages = [self.purchased_product.product.package]

    def add_to_solr(self):
        if not self.is_approved:
            return
        else:
            return super(PurchasedJob, self).add_to_solr()


def on_delete(sender, instance, **kwargs):
    """
    Ensures that an object is successfully removed from solr when it is deleted,
    and prevents deletion if it can't be removed from solr for some reason.

    """
    instance.remove_from_solr()
pre_delete.connect(on_delete, sender=Job)
pre_delete.connect(on_delete, sender=PurchasedJob)


class PackageMixin(object):
    def user_available(self):
        """
        Filters out anything that shouldn't be available to the user.
        Right now this is just handling SeoSite- and Company-specific
        SitePackages.

        In the future, as more models inherit off of Package,
        this will need to handle more subclasses better.

        """
        sitepackage_kwargs = {
            'sitepackage__isnull': False,
            'sitepackage__seosite__isnull': True,
            'sitepackage__company__isnull': True,
        }
        return self.filter(**sitepackage_kwargs)

    def filter_company(self, company_list):
        attributes = Package.get_related_attributes()
        key = '{field}__owner_id'
        q_list = []
        for company in company_list:
            [q_list.append(models.Q(**{key.format(field=attribute): company.id}))
             for attribute in attributes]
        result = self.filter(reduce(operator.or_, q_list))
        return result


class PackageQuerySet(QuerySet, PackageMixin):
    pass


class PackageManager(models.Manager, PackageMixin):
    def get_query_set(self):
        return PackageQuerySet(self.model, using=self._db)


class Package(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType)
    # There is also code that makes the assumption that the owner field
    # exists. Because SitePackage doesn't require an owner field (but other
    # package types likely will require an owner field) there's no good
    # way to force the existance of this field.
    # owner = models.ForeignKey('mydashboard.Company')

    objects = PackageManager()

    def __unicode__(self):
        name = "{content_type} - {name}"
        return name.format(content_type=self.content_type.name.title(),
                           name=self.name)

    def save(self, *args, **kwargs):
        if not hasattr(self, 'content_type') or not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        super(Package, self).save(*args, **kwargs)

    def get_model_name(self):
        return self.content_type.model

    @staticmethod
    def get_related_attributes():
        related_attrs = []
        subclasses = Package.__subclasses__()
        package_fields = ['name', 'content_type', 'id']
        fields = Package._meta.init_name_map()
        for key, value in fields.items():
            if key not in package_fields and value[0].model in subclasses:
                related_attrs.append(key)
        return related_attrs


class SitePackageManager(models.Manager):
    def user_available(self):
        """
        Filters out anything that shouldn't be available to the user.

        """
        sitepackage_kwargs = {
            'seosite__isnull': True,
            'company__isnull': True,
        }
        return self.filter(**sitepackage_kwargs)


class SitePackage(Package):
    objects = SitePackageManager()

    sites = models.ManyToManyField('mydashboard.SeoSite', null=True)
    owner = models.ForeignKey('mydashboard.Company', null=True, blank=True,
                              help_text='The owner of this site package. '
                                        'This should only be used if the '
                                        'site package will be used by '
                                        'the company for partner microsites.')

    def get_model_name(self):
        return self.__class__.__name__

    def user_has_access(self, user):
        """
        The base user_has_access() is not sufficient in situations where
        no owner Company has been specified.

        """
        if self.owner:
            return super(SitePackage, self).user_has_access(user)
        else:
            user_companies = user.get_companies()
            for site in self.sites.all():
                for company in site.get_companies():
                    if company not in user_companies:
                        return False
        return True

    def make_unique_for_site(self, seo_site):
        """
        Associates a SitePackage instance with a specific SeoSite. This
        should only be used when the SitePackage applies only to a single
        SeoSite. This removes all previous SeoSite relationships.

        """
        if not self.pk:
            self.save()
        self.sites = [seo_site]
        self.name = seo_site.domain
        seo_site.site_package = self
        seo_site.save()
        self.save()

    def make_unique_for_company(self, company):
        """
        Associates a SitePackage instance with a specific SeoSite. This
        should only be used when the SitePackage applies only to a single
        SeoSite. This removes all previous SeoSite relationships.

        """
        if not self.pk:
            self.save()
        self.sites = company.get_seo_sites()
        self.name = company.name
        company.site_package = self
        company.save()
        self.save()


class PurchasedProduct(BaseModel):
    product = models.ForeignKey('Product')

    owner = models.ForeignKey('mydashboard.Company')
    purchase_date = models.DateField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    paid = models.BooleanField(default=True)

    expiration_date = models.DateField()
    num_jobs_allowed = models.IntegerField()
    jobs_remaining = models.IntegerField()

    transaction = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255, verbose_name='First Name')
    last_name = models.CharField(max_length=255, verbose_name='Last Name')
    address_line_one = models.CharField(max_length=255,
                                        verbose_name='Address Line One')
    address_line_two = models.CharField(max_length=255, blank=True,
                                        verbose_name='Address Line Two')
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)

    def save(self, **kwargs):
        length = self.product.posting_window_length
        self.num_jobs_allowed = self.product.num_jobs_allowed
        if not hasattr(self, 'pk') or not self.pk:
            self.expiration_date = date.today() + timedelta(length)
            self.jobs_remaining = self.num_jobs_allowed
        super(PurchasedProduct, self).save(**kwargs)


class ProductGrouping(BaseModel):
    class Meta:
        ordering = ['display_order']

    help_text = {
        'explanation': 'The explanation of the grouping as it will be '
                       'displayed to the user.',
        'display_order': 'The position in which this group will be '
                         'displayed to the customer on the product group '
                         'page.',
        'display_title': 'The product grouping title as it will be displayed '
                         'to the user.',
        'name': 'The "short" name of the product grouping. This is only used '
                'in the admin.',
        'products': 'The products you want displayed with this grouping.',
    }

    products = models.ManyToManyField('Product', null=True,
                                      through='ProductOrder',
                                      help_text=help_text['products'])
    display_order = models.IntegerField(default=0,
                                        help_text=help_text['display_order'],
                                        verbose_name='Display Order')
    display_title = models.CharField(max_length=255,
                                     help_text=help_text['display_title'],
                                     verbose_name='Display Title')
    explanation = models.TextField(help_text=help_text['explanation'])
    name = models.CharField(max_length=255, help_text=help_text['name'])
    owner = models.ForeignKey('mydashboard.Company')

    def __unicode__(self):
        return self.name


class ProductOrder(models.Model):
    class Meta:
        unique_together = ('product', 'group', )
    product = models.ForeignKey('Product')
    group = models.ForeignKey('ProductGrouping')
    display_order = models.PositiveIntegerField(default=0)


class Product(BaseModel):
    posting_window_choices = ((30, '30 Days'), (60, '60 Days'),
                              (90, '90 Days'), (365, '1 Year'), )
    max_job_length_choices = ((15, '15 Days'), (30, '30 Days'), (60, '60 Days'),
                              (90, '90 Days'), (365, '1 Year'), )

    help_text = {
        'cost': 'How much this product should cost.',
        'is_archived': '',
        'is_displayed': 'Products should not show up in the online '
                        'product lists.',
        'max_job_length': 'Number of days each job may appear.',
        'num_jobs_allowed': 'The number of jobs that can be posted.',
        'posting_window_length': 'The number of days the customer has to '
                                 'post jobs.',
        'requires_approval': 'Jobs posted will require administrator approval.'
    }

    package = models.ForeignKey('Package')
    owner = models.ForeignKey('mydashboard.Company')

    name = models.CharField(max_length=255, blank=True)
    cost = models.DecimalField(max_digits=20, decimal_places=2,
                               verbose_name='Product Price',
                               help_text=help_text['cost'])
    posting_window_length = models.IntegerField(default=30,
                                                choices=posting_window_choices,
                                                help_text=help_text['posting_window_length'],
                                                verbose_name='Posting Window Duration')
    max_job_length = models.IntegerField(default=30,
                                         choices=max_job_length_choices,
                                         help_text=help_text['max_job_length'],
                                         verbose_name='Maximum Job Duration')
    num_jobs_allowed = models.IntegerField(default=5, help_text=help_text['num_jobs_allowed'],
                                           verbose_name='Number of Jobs')

    description = models.TextField(verbose_name='Product Description')
    featured = models.BooleanField(default=False)
    requires_approval = models.BooleanField(help_text=help_text['requires_approval'],
                                            verbose_name='Requires Approval',
                                            default=True)

    is_archived = models.BooleanField(help_text=help_text['is_archived'],
                                      verbose_name='Archived', default=False)
    is_displayed = models.BooleanField(help_text=help_text['is_displayed'],
                                       verbose_name='Displayed', default=False)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.name
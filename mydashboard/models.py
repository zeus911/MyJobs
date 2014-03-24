from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.contrib.auth.models import Group
from django.db import models

from myjobs.models import User


class Company(models.Model):
    """
    Companies are the central hub for a group of modules and employers.

    *** Why isn't the primary key an auto incrementing field? ***
    To keep the my.jobs Company model in sync with the microsites Company
    model the id is the same to ease the transition to a single model down the
    line.

    """
    id = models.IntegerField(primary_key=True)
    admins = models.ManyToManyField(User, through='CompanyUser')
    name = models.CharField('Name', max_length=200, unique=True)
    job_source_ids = models.ManyToManyField('BusinessUnit')
    member = models.BooleanField('DirectEmployers Association Member',
                                 default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'seo_company'
        verbose_name_plural = 'companies'

    def slugified_name(self):
        return slugify(self.name)


class SeoSite(Site):
    business_units = models.ManyToManyField('BusinessUnit', null=True,
                                            blank=True)
    site_title = models.CharField('Site Title', max_length=200, blank=True,
                                  default='')
    view_sources = models.ForeignKey('ViewSource', null=True, blank=True)

    class Meta:
        db_table = 'seo_seosite'
        verbose_name = 'seo site'
        verbose_name_plural = 'seo sites'


class ViewSource(models.Model):
    name = models.CharField(max_length=200, default='')
    view_source = models.IntegerField(max_length=20, default='')

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.view_source)

    class Meta:
        db_table = 'seo_viewsource'


class BusinessUnit(models.Model):
    id = models.IntegerField('Business Unit Id', max_length=10,
                             primary_key=True)
    title = models.CharField(max_length=500, null=True, blank=True)

    def __unicode__(self):
        return '%s: %s' % (self.title, str(self.id))

    class Meta:
        db_table = 'seo_businessunit'


class CandidateEvent(models.Model):
    """
    Something happened! This log tracks job views and saved searches.
    
    """
    who = models.ForeignKey(User)
    whom = models.ForeignKey(Company)
    what = models.CharField(max_length=255)
    where = models.URLField(max_length=300)
    when = models.DateTimeField(auto_now=True)


class DashboardModule(models.Model):
    company = models.ForeignKey(Company)


class Microsite(models.Model):
    url = models.URLField(max_length=300)
    company = models.ForeignKey(Company)

    def __unicode__(self):
        return 'Microsite %s for %s' % (self.url, self.company.name)


class CompanyUser(models.Model):
    GROUP_NAME = 'Employer'

    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)
    date_added = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return 'Admin %s for %s' % (self.user.email, self.company.name)

    def save(self, *args, **kwargs):
        """
        Adds the user to the Employer group if it wasn't already a member.

        If the user is already a member of the Employer group, the Group app
        is smart enough to not add it a second time.
        """
        group = Group.objects.get(name=self.GROUP_NAME)
        self.user.groups.add(group)

        super(CompanyUser,self).save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'company')

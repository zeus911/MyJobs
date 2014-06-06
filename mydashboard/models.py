from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.contrib.auth.models import Group
from django.db import models

from myjobs.models import User
from postajob.models import SitePackage


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
    site_package = models.ForeignKey(SitePackage, null=True,
                                     on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'seo_company'
        verbose_name_plural = 'companies'

    def slugified_name(self):
        return slugify(self.name)

    def get_seo_sites(self):
        """
        Retrieves a given company's microsites

        Inputs:
        :company: Company whose microsites are being retrieved

        Outputs:
        :microsites: List of microsites
        :buids: List of buids associated with the company's microsites
        """
        job_source_ids = self.job_source_ids.all()
        buids = job_source_ids.values_list('id', flat=True)
        microsites = SeoSite.objects.filter(business_units__in=buids)
        return microsites

    def user_has_access(self, user):
        """
        In order for a user to have access they must be a CompanyUser
        for the Company.
        """
        return user in self.admins.all()


class SeoSite(Site):
    business_units = models.ManyToManyField('BusinessUnit', null=True,
                                            blank=True)
    site_title = models.CharField('Site Title', max_length=200, blank=True,
                                  default='')
    view_sources = models.ForeignKey('ViewSource', null=True, blank=True)
    site_package = models.ForeignKey(SitePackage, null=True,
                                     on_delete=models.SET_NULL)

    class Meta:
        db_table = 'seo_seosite'
        verbose_name = 'seo site'
        verbose_name_plural = 'seo sites'

    def user_has_access(self, user):
        """
        In order for a user to have access they must be a CompanyUser
        for the Company that owns the SeoSite.
        """
        site_buids = self.business_units.all()
        companies = Company.objects.filter(job_source_ids__in=site_buids)
        user_companies = user.get_companies()
        for company in companies:
            if company not in user_companies:
                return False
        return True

    def get_companies(self):
        site_buids = self.business_units.all()
        return Company.objects.filter(job_source_ids__in=site_buids).distinct()


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

        return super(CompanyUser, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'company')

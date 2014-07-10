from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.contrib.auth.models import Group
from django.db import models

from myjobs.models import User
from postajob.models import SitePackage


class Company(models.Model):
    """
    This model defines companies that come from various job sources (currently
    business units).

    """
    def __unicode__(self):
        return "%s" % self.name

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']
        db_table = 'seo_company'

    def save(self, *args, **kwargs):
        self.company_slug = slugify(self.name)
        super(Company, self).save(*args, **kwargs)

    def associated_jobs(self):
        b_units = self.job_source_ids.all()
        job_count = 0
        for unit in b_units:
            job_count += unit.associated_jobs
        return job_count

    def featured_on(self):
        return ", ".join(self.seosite_set.all().values_list("domain",
                                                            flat=True))
    admins = models.ManyToManyField(User, through='CompanyUser')
    site_package = models.ForeignKey(SitePackage, null=True,
                                     on_delete=models.SET_NULL)
    name = models.CharField('Name', max_length=200, unique=True)
    company_slug = models.SlugField('Company Slug', max_length=200, null=True,
                                    blank=True)
    job_source_ids = models.ManyToManyField('BusinessUnit')
    logo_url = models.URLField('Logo URL', max_length=200, null=True,
                               blank=True, help_text="The url for the 100x50 "
                                                     "logo image for this "
                                                     "company.")
    linkedin_id = models.CharField('LinkedIn Company ID',
                                   max_length=20, null=True, blank=True,
                                   help_text="The LinkedIn issued company "
                                             "ID for this company.")
    og_img = models.URLField('Open Graph Image URL', max_length=200, null=True,
                             blank=True, help_text="The url for the large "
                                                   "format logo for use when "
                                                   "sharing jobs on "
                                                   "LinkedIn, and other social "
                                                   "platforms that support"
                                                   " OpenGraph.")
    canonical_microsite = models.URLField('Canonical Microsite URL',
                                          max_length=200, null=True, blank=True,
                                          help_text="The primary "
                                                    "directemployers microsite "
                                                    "for this company.")
    member = models.BooleanField('DirectEmployers Association Member',
                                 default=False)
    digital_strategies_customer = models.BooleanField('Digital Strategies '
                                                      'Customer', default=False)
    enhanced = models.BooleanField('Enhanced', default=False)

    # Permissions
    prm_access = models.BooleanField(default=True)
    product_access = models.BooleanField(default=False)
    user_created = models.BooleanField(default=False)

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
    ADMIN_GROUP_NAME = 'Purchased Microsite Admin'

    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)
    date_added = models.DateTimeField(auto_now=True)
    group = models.ManyToManyField('auth.Group', blank=True)

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

    def make_purchased_microsite_admin(self):
        group, _ = Group.objects.get_or_create(name=self.ADMIN_GROUP_NAME)
        print group
        self.group.add(group)
        self.save()
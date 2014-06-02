from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator
from django.forms import (CharField, CheckboxSelectMultiple, ModelForm,
                          ModelMultipleChoiceField, RadioSelect,
                          Select, TextInput)

from mydashboard.models import SeoSite
from mypartners.widgets import SplitDateDropDownField
from postajob.models import Job, SitePackage


class JobForm(ModelForm):
    class Meta:
        exclude = ('guid', 'country_short', 'state_short', 'is_syndicated', )
        fields = ('title', 'is_syndicated', 'reqid', 'description', 'city',
                  'state', 'country', 'zipcode', 'date_expired', 'is_expired',
                  'autorenew', 'apply_type', 'apply_link', 'apply_email',
                  'apply_info', 'company', 'post_to', 'site_packages', )
        model = Job

    class Media:
        css = {
            'all': ('postajob.153-05.css', )
        }
        js = ('postajob.153-05.js', )

    apply_choices = [('link', "Link"), ('email', 'Email'),
                     ('instructions', 'Instructions')]
    apply_type = CharField(label='Application Method',
                           widget=RadioSelect(choices=apply_choices),
                           help_text=Job.help_text['apply_type'])

    apply_email = CharField(required=False, max_length=255,
                            label='Apply Email',
                            widget=TextInput(attrs={'size': 50}),
                            help_text=Job.help_text['apply_email'])
    apply_link = CharField(required=False, max_length=255,
                           label='Apply Link',
                           help_text=Job.help_text['apply_link'],
                           widget=TextInput(attrs={'rows': 1, 'size': 50}))

    # For a single job posting by a member company to a microsite
    # we consider each site an individual site package but the
    # site_package for a site is only created when it's first used,
    # so we use SeoSite as the queryset here instead of SitePackage.
    site_packages_widget = admin.widgets.FilteredSelectMultiple('Sites', False)
    site_packages = ModelMultipleChoiceField(SeoSite.objects.all(),
                                             label="Site",
                                             required=False,
                                             widget=site_packages_widget)
    country = CharField(widget=Select(choices=Job.get_country_choices()),
                        help_text=Job.help_text['country'],
                        initial='United States of America')
    state = CharField(label='State', help_text=Job.help_text['state'],
                      widget=Select(choices=Job.get_state_choices()))
    date_expired = SplitDateDropDownField(label="Expires On",
                                          help_text=Job.help_text['date_expired'])
    post_to_choices = [('network', 'The entire My.jobs network'),
                       ('site', 'A specific site you own'), ]
    post_to = CharField(label='Post to', help_text=Job.help_text['post_to'],
                        widget=RadioSelect(attrs={'id': 'post-to-selector'},
                                           choices=post_to_choices),
                        initial='site')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(JobForm, self).__init__(*args, **kwargs)
        # Prevent all three apply options from being show on the page at
        # once.
        if self.instance and self.instance.apply_info:
            self.initial['apply_type'] = 'instructions'
        else:
            self.initial['apply_type'] = 'link'
        if not self.request.path.startswith('/admin'):
            # FilteredSelectMultiple doesn't work outside the admin, so
            # switch to a widget that does work.
            self.fields['site_packages'].widget = CheckboxSelectMultiple(
                attrs={'class': 'job-sites-checkbox'})
            # After changing the widget the queryset also needs reset.
            self.fields['site_packages'].queryset = SeoSite.objects.all()
        if not self.request.user.is_superuser:
            # Limit a user's access to only companies/sites they own.
            kwargs = {'admins': self.request.user}
            self.fields['company'].queryset = \
                self.fields['company'].queryset.filter(**kwargs)
            kwargs = {'business_units__company__admins': self.request.user}
            self.fields['site_packages'].queryset = \
                self.fields['site_packages'].queryset.filter(**kwargs).distinct()

        # Since we're not using actual site_packages for the site_packages,
        # the initial data also needs to be manually set.
        if self.instance.site_packages:
            packages = self.instance.site_packages.all()
            self.initial['site_packages'] = [str(site.pk) for site in
                                             self.instance.on_sites()]
            # If the only site package is the
            if (packages.count() == 1 and
                    packages[0] == self.instance.company.site_package):
                self.initial['post_to'] = 'network'

    def clean_apply_link(self):
        """
        If the apply_link is a url and not a mailto, format the link
        appropriately and confirm it really is a url.

        """
        apply_link = self.cleaned_data.get('apply_link')
        if apply_link and apply_link.startswith('mailto:'):
            return apply_link
        if apply_link and not (apply_link.startswith('http://') or
                               apply_link.startswith('https://')):
            apply_link = 'http://{link}'.format(link=apply_link)
        if apply_link:
            URLValidator(apply_link)
        return apply_link

    def clean_site_packages(self):
        """
        Convert from SeoSite to a SitePackage.

        """
        if self.cleaned_data.get('post_to') == 'network':
            return None

        sites = self.cleaned_data.get('site_packages')
        site_packages = []
        for site in sites:
            if not site.site_package:
                # If a site doesn't already have a site_package specific
                # to it create one.
                package = SitePackage(name=site.domain)
                package.make_unique_for_site(site)
            site_packages.append(site.site_package)

        return site_packages

    def clean(self):
        apply_info = self.cleaned_data.get('apply_info')
        apply_link = self.cleaned_data.get('apply_link')
        apply_email = self.cleaned_data.get('apply_email')
        post_to = self.cleaned_data.get('post_to')

        # clean() is run after clean_site_packages(), allowing
        # overriding the 'None' that cleaned_data should've been
        # set to during clean_site_packages().
        if post_to == 'network':
            company = self.cleaned_data.get('company')

            if not company.site_package:
                package = SitePackage()
                package.make_unique_for_company(company)
            self.cleaned_data['site_packages'] = [company.site_package]

        # Require one set of apply instructions.
        if not apply_info and not apply_link and not apply_email:
            raise ValidationError('You must supply some type of appliction '
                                  'information.')
        # Allow only one set of apply instructions.
        if sum([1 for x in [apply_info, apply_link, apply_email] if x]) > 1:
            raise ValidationError('You can only supply one application '
                                  'method.')

        if apply_email:
            # validate_email() raises its own ValidationError.
            validate_email(apply_email)
            # If the apply instructions are an email, it needs to be
            # reformatted as a mailto and saved as the link.
            apply_email = 'mailto:{link}'.format(link=apply_email)
            self.cleaned_data['apply_link'] = apply_email

        return self.cleaned_data

    def save(self, commit=True):
        sites = self.cleaned_data['site_packages']
        job = super(JobForm, self).save(commit)

        country = job.country
        state = job.state
        try:
            job.state_short = Job.get_state_map()[state]
        except IndexError:
            job.state_short = None
        try:
            job.country_short = Job.get_country_map()[country]
        except IndexError:
            job.country_short = None

        # The object must have a primary key before the many-to-many
        # relationship can be created.
        if not job.pk:
            job.save()
        [job.site_packages.add(s) for s in sites]
        return job


class SitePackageForm(ModelForm):
    class Meta:
        model = SitePackage

    sites_widget = admin.widgets.FilteredSelectMultiple('Sites', False)
    sites = ModelMultipleChoiceField(SeoSite.objects.all(),
                                     label="On Sites",
                                     required=False,
                                     widget=sites_widget)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SitePackageForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_superuser:
            # Limit a user's access to only sites they own.
            kwargs = {'business_units__company__admins': self.request.user}
            self.fields['sites'].queryset = \
                self.fields['sites'].queryset.filter(**kwargs).distinct()
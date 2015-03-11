from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpResponseRedirect
from django.template import Template, RequestContext
from django.template.loaders.filesystem import Loader
from django.utils.safestring import mark_safe

from myblocks import context_tools
from myblocks.helpers import success_url
from myjobs.helpers import expire_login
from myjobs.models import User
from registration.forms import CustomAuthForm, RegistrationForm


def raw_base_template(obj):
    loader = Loader()
    return loader.load_template_source(obj.base_template)[0]


class Block(models.Model):
    base_template = None

    content_type = models.ForeignKey(ContentType, editable=False)
    name = models.CharField(max_length=255)
    offset = models.PositiveIntegerField()
    span = models.PositiveIntegerField()
    template = models.TextField()
    head = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def bootstrap_classes(self):
        offset = "col-md-offset-%s" % self.offset if self.offset else ''
        span = "col-md-%s" % self.span if self.span else ''
        return " ".join([offset, span])

    def block_size(self):
        return self.offset + self.span

    def cast(self):
        """
        Casts the block to the appropriate subclass.

        """
        return self.content_type.get_object_for_this_type(pk=self.pk)

    def context(self, request):
        return {}

    def get_template(self):
        return '<div class="block-%s %s">%s</div>' % (self.id,
                                                      self.bootstrap_classes(),
                                                      self.template)

    def required_js(self):
        return []

    def save(self, *args, **kwargs):
        if not self.id:
            # Set content_type so the object can later be cast back to
            # its subclass.
            self.content_type = self._get_real_type()
        super(Block, self).save(*args, **kwargs)


class BreadboxBlock(Block):
    base_template = 'myblocks/blocks/breadbox.html'

    def context(self, request):
        return {
            'breadbox': context_tools.get_breadbox(request)
        }


class ColumnBlock(Block):
    base_template = None

    blocks = models.ManyToManyField('Block', through='ColumnBlockOrder',
                                    related_name='included_blocks')

    def context(self, request):
        context = {}
        for block in self.blocks.all():
            context.update(block.context(request))
        return context

    def get_template(self):
        blocks = []
        for block in self.blocks.all().order_by('columnblockorder__order'):
            blocks.append('<row>%s</row>' % block.get_template())

        return '<div class="block-%s %s">%s</div>' % (self.id,
                                                      self.bootstrap_classes(),
                                                      ''.join(blocks))

    def required_js(self):
        js = []
        for block in self.blocks.all():
            js += block.cast().required_js()
        return js


class ContentBlock(Block):
    base_template = 'myblocks/blocks/content.html'


class LoginBlock(Block):
    base_template = 'myblocks/blocks/login.html'

    def context(self, request):
        querystring = "?%s" % request.META.get('QUERY_STRING')
        if request.POST and self.submit_btn_name() in request.POST:
            # If data is being posted to this specific block, give the form
            # the opportunity to render any errors.
            return {
                'login_action': querystring,
                'login_form': CustomAuthForm(data=request.POST),
                'login_submit_btn_name': self.submit_btn_name()
            }
        return {
            'login_action': querystring,
            'login_form': CustomAuthForm(),
            'login_submit_btn_name': self.submit_btn_name()
        }

    def handle_post(self, request):
        # Confirm that the requst is a post, and that this form is
        # the intended recipient of the posted data.
        if not request.POST or self.submit_btn_name() not in request.POST:
            return None

        form = CustomAuthForm(data=request.POST)
        if form.is_valid():
            # Log in the user and redirect based on the success_url rules.
            expire_login(request, form.get_user())

            response = HttpResponseRedirect(success_url(request))
            response.set_cookie('myguid', form.get_user().user_guid,
                                expires=365*24*60*60, domain='.my.jobs')
            return response
        return None

    def submit_btn_name(self):
        return 'login-%s' % self.id


class MoreButtonBlock(Block):
    base_template = 'myblocks/blocks/morebutton.html'

    def context(self, request):
        return {
            'arranged_jobs': context_tools.get_arranged_jobs(request),
            'data_type': '',
            'num_default_jobs': len(context_tools.get_default_jobs(request)),
            'num_featured_jobs': len(context_tools.get_featured_jobs(request)),
            'site_config': context_tools.get_site_config(request),
        }

    def required_js(self):
        return ['%spager.160-29.js' % settings.STATIC_URL]


class RegistrationBlock(Block):
    base_template = 'myblocks/blocks/registration.html'

    def context(self, request):
        querystring = "?%s" % request.META.get('QUERY_STRING')
        if request.POST and self.submit_btn_name() in request.POST:
            # If data is being posted to this specific block, give the form
            # the opportunity to render any errors.
            return {
                'registration_action': querystring,
                'qs': querystring,
                'registration_form': RegistrationForm(request.POST,
                                                      auto_id=False),
                'registration_submit_btn_name': self.submit_btn_name(),
            }
        return {
            'registration_action': querystring,
            'registration_form': RegistrationForm(),
            'registration_submit_btn_name': self.submit_btn_name(),
        }

    def handle_post(self, request):
        # Confirm that the requst is a post, and that this form is
        # the intended recipient of the posted data.
        if not request.POST or self.submit_btn_name() not in request.POST:
            return None
        form = RegistrationForm(request.POST, auto_id=False)
        if form.is_valid():
            # Create a user, log them in, and redirect based on the
            # success_url rules.
            user, created = User.objects.create_user(request=request,
                                                     send_email=True,
                                                     **form.cleaned_data)
            user_cache = authenticate(
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password1'])
            expire_login(request, user_cache)

            response = HttpResponseRedirect(success_url(request))
            response.set_cookie('myguid', user.user_guid, expires=365*24*60*60,
                                domain='.my.jobs')
            return response
        return None

    def submit_btn_name(self):
        return 'registration-%s' % self.id


class SavedSearchWidgetBlock(Block):
    base_template = 'myblocks/blocks/savedsearchwidget.html'

    def required_js(self):
        return ['//d2e48ltfsb5exy.cloudfront.net/myjobs/tools/def.myjobs.widget.153-05.js']


class SearchBoxBlock(Block):
    base_template = 'myblocks/blocks/searchbox.html'

    def context(self, request):
        return {
            'location_term': context_tools.get_location_term(request),
            'moc_term': context_tools.get_moc_term(request),
            'moc_id_term': context_tools.get_moc_id_term(request),
            'search_url': context_tools.get_search_url(request),
            'site_config': context_tools.get_site_config(request),
            'title_term': context_tools.get_title_term(request),
            'total_jobs_count': context_tools.get_total_jobs_count(request),
        }


class SearchFilterBlock(Block):
    base_template = 'myblocks/blocks/searchfilter.html'

    def context(self, request):
        return {
            'widgets': context_tools.get_widgets(request)
        }

    def required_js(self):
        return ['%spager.160-29.js' % settings.STATIC_URL]


class SearchResultBlock(Block):
    base_template = 'myblocks/blocks/searchresult.html'

    def context(self, request):
        return {
            'arranged_jobs': context_tools.get_arranged_jobs(request),
            'data_type': '',
            'default_jobs': context_tools.get_default_jobs(request),
            'featured_jobs': context_tools.get_featured_jobs(request),
            'location_term': context_tools.get_location_term(request),
            'moc_term': context_tools.get_moc_term(request),
            'query_string': context_tools.get_query_string(request),
            'site_commitments_string': context_tools.get_site_commitments_string(request),
            'site_config': context_tools.get_site_config(request),
            'site_tags': settings.SITE_TAGS,
            'title_term': context_tools.get_title_term(request),
        }


class ShareBlock(Block):
    base_template = 'myblocks/blocks/share.html'


class VeteranSearchBox(Block):
    base_template = 'myblocks/blocks/veteransearchbox.html'

    def context(self, request):
        return {
            'location_term': context_tools.get_location_term(request),
            'moc_term': context_tools.get_moc_term(request),
            'moc_id_term': context_tools.get_moc_id_term(request),
            'search_url': context_tools.get_search_url(request),
            'site_config': context_tools.get_site_config(request),
            'title_term': context_tools.get_title_term(request),
            'total_jobs_count': context_tools.get_total_jobs_count(request),
        }


class Row(models.Model):
    blocks = models.ManyToManyField('Block', through='BlockOrder')

    def __unicode__(self):
        return ', '.join([block.name for block in self.blocks.all()])

    @staticmethod
    def bootstrap_classes():
        return "row"

    def context(self):
        return {}

    def get_template(self):
        blocks = [block.get_template()
                  for block in self.blocks.all().order_by('blockorder__order')]

        return '<row>%s</row>' % ''.join(blocks)


class Page(models.Model):
    base_template = 'myblocks/myblocks_base.html'

    HOME_PAGE = 'home_page'
    SEARCH_RESULTS = 'search_results'
    LOGIN = 'login'

    PRODUCTION = 'production'
    STAGING = 'staging'

    page_type_choices = (
        # (HOME_PAGE, 'Home Page'),
        (SEARCH_RESULTS, 'Job Search Results Page'),
        (LOGIN, 'Login Page'),
    )
    page_status_choices = (
        (STAGING, 'Staging'),
        (PRODUCTION, 'Production'),
    )

    page_type = models.CharField(choices=page_type_choices, max_length=255)
    rows = models.ManyToManyField('Row', through='RowOrder')
    site = models.ForeignKey('seo.SeoSite')
    status = models.CharField(choices=page_status_choices, max_length=255,
                              default='production')

    head = models.TextField(blank=True)

    def __unicode__(self):
        return "%s for %s: %s" % (self.page_type, self.site.name, self.pk)

    def all_blocks(self):
        """
        Gets a list of every unique block included in a page.

        """
        query = (models.Q(row__page=self) |
                 models.Q(columnblockorder__column_block__row__page=self))
        return [block.cast() for block in Block.objects.filter(query).distinct()]

    def bootstrap_classes(self):
        return "col-md-12"

    def context(self, request):
        context = {}
        for block in self.all_blocks():
            context.update(block.context(request))
        return context

    def get_body(self):
        rows = []
        for row in self.rows.all().order_by('roworder__order'):
            rows.append(row.get_template())
        return ''.join(rows)

    def get_head(self):
        blocks = self.all_blocks()
        head = [block.head for block in blocks]
        additional_js = []
        for block in self.all_blocks():
            additional_js += [self.to_js_tag(js) for js in block.required_js()]
        head += list(set(additional_js))
        print additional_js
        return self.head + ''.join(head)

    def get_template(self):
        from django.template import Template, Context
        context = {
            'body': mark_safe(self.get_body()),
            'head': mark_safe(self.get_head()),
            'page': self,
            'STATIC_URL': settings.STATIC_URL,
        }
        template = Template(raw_base_template(self))
        return template.render(Context(context))

    def render(self, request):
        context = self.context(request)
        template = Template(self.get_template())
        return template.render(RequestContext(request, context))

    def templatetag_library(self):
        templatetags = ['{% load seo_extras %}', '{% load i18n %}',
                        '{% load highlight %}', '{% load humanize %}']
        return ' '.join(templatetags)

    def to_js_tag(self, js_file):
        return '<script type="text/javascript" src="%s"></script>' % js_file


class BlockOrder(models.Model):
    block = models.ForeignKey('Block')
    row = models.ForeignKey('Row')
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ('order', )


class ColumnBlockOrder(models.Model):
    block = models.ForeignKey('Block')
    column_block = models.ForeignKey('ColumnBlock',
                                     related_name='included_column_blocks')
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ('order', )


class RowOrder(models.Model):
    row = models.ForeignKey('Row')
    order = models.PositiveIntegerField()
    page = models.ForeignKey('Page')

    class Meta:
        ordering = ('order', )

    def __unicode__(self):
        return "Row for page %s" % self.page.pk
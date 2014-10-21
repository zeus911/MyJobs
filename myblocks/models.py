from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from myblocks.helpers import get_jobs, success_url
from myjobs.helpers import expire_login
from myjobs.models import User
from registration.forms import CustomAuthForm, RegistrationForm


class Block(models.Model):
    content_type = models.ForeignKey(ContentType)
    name = models.CharField(max_length=255)
    offset = models.PositiveIntegerField()
    span = models.PositiveIntegerField()

    def __unicode__(self):
        return self.name

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def bootstrap_classes(self):
        offset = "offset%s" % self.offset if self.offset else ''
        span = "span%s" % self.span if self.span else ''

        return "%s %s" % (offset, span)

    def block_size(self):
        return self.offset + self.span

    def cast(self):
        """
        Casts the block to the appropriate subclass.

        """

        return self.content_type.get_object_for_this_type(pk=self.pk)

    def context(self, request):
        return {
            'block': self,
            'request': request
        }

    def render(self, request):
        """
        Generates the html corresponding to the block.

        """

        html = render_to_string(self.cast().template(), self.context(request),
                                context_instance=RequestContext(request))
        return mark_safe(html)

    def save(self, *args, **kwargs):
        if not self.id:
            # Set content_type so the object can later be cast back to
            # its subclass.
            self.content_type = self._get_real_type()
        super(Block, self).save(*args, **kwargs)


class ContentBlock(Block):
    content = models.TextField()

    @staticmethod
    def template():
        return 'myblocks/blocks/content.html'


class ImageBlock(Block):
    image_url = models.URLField(max_length=200)

    def context(self, request):
        return {
            'block': self,
            'request': request,
            'site': settings.SITE,
        }

    @staticmethod
    def template():
        return 'myblocks/blocks/image.html'


class LoginBlock(Block):
    def context(self, request):
        querystring = "?%s" % request.META.get('QUERY_STRING')
        if request.POST and self.submit_btn_name() in request.POST:
            # If data is being posted to this specific block, give the form
            # the opportunity to render any errors.
            return {
                'action': querystring,
                'block': self,
                'login_form': CustomAuthForm(data=request.POST),
                'request': request,
            }
        return {
            'action': querystring,
            'block': self,
            'login_form': CustomAuthForm(),
            'request': request,
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

    @staticmethod
    def template():
        return 'myblocks/blocks/login.html'


class RegistrationBlock(Block):
    def context(self, request):
        querystring = request.META.get('QUERY_STRING')
        if request.POST and self.submit_btn_name() in request.POST:
            # If data is being posted to this specific block, give the form
            # the opportunity to render any errors.
            return {
                'action': querystring,
                'block': self,
                'qs': querystring,
                'registration_form': RegistrationForm(request.POST,
                                                      auto_id=False),
                'request': request,
            }
        return {
            'action': querystring,
            'block': self,
            'registration_form': RegistrationForm(),
            'request': request,
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

    @staticmethod
    def template():
        return 'myblocks/blocks/registration.html'


class SavedSearchWidgetBlock(Block):
    @staticmethod
    def template():
        return 'myblocks/blocks/savedsearchwidget.html'


class SearchBoxBlock(Block):
    search_box_templates = (
        ('myblocks/blocks/searchbox.html', 'Basic Search Box'),
        ('myblocks/blocks/veteransearchbox.html', 'Veteran Search Box'),
    )

    search_box_template = models.CharField(max_length=255,
                                           choices=search_box_templates)

    def template(self):
        return self.search_box_template


class SearchFilterBlock(Block):
    def context(self, request):
        data = get_jobs(request)
        data['block'] = self
        return data

    @staticmethod
    def template():
        return 'myblocks/blocks/searchfilter.html'


class SearchResultBlock(Block):
    def context(self, request):
        data = get_jobs(request)
        data['block'] = self
        return data

    @staticmethod
    def template():
        return 'myblocks/blocks/searchresult.html'


class ShareBlock(Block):
    @staticmethod
    def template():
        return 'myblocks/blocks/share.html'


class ColumnBlock(Block):
    blocks = models.ManyToManyField('Block', through='ColumnBlockOrder',
                                    related_name='included_blocks')

    def context(self, request):
        row = '<div class="row">%s</div>'

        html = [row % block.cast().render(request) for
                block in self.blocks.all().order_by('columnblockorder__order')]
        return {
            'block': self,
            'content': mark_safe(''.join(html)),
            'request': request
        }

    @staticmethod
    def template():
        return 'myblocks/blocks/columnblock.html'


class Row(models.Model):
    blocks = models.ManyToManyField('Block', through='BlockOrder')

    def __unicode__(self):
        return ', '.join([block.name for block in self.blocks.all()])

    @staticmethod
    def boostrap_classes():
        return "row"

    def context(self, request):
        content = []
        for block in self.blocks.all().order_by('blockorder__order'):
            content.append(block.cast().render(request))
        return {
            'row': self,
            'content': mark_safe(''.join(content)),
            'request': request,
        }

    def render(self, request):
        html = render_to_string('myblocks/row_base.html',
                                self.context(request))
        return mark_safe(html)


class Page(models.Model):
    bootstrap_choices = (
        (1, 'Bootstrap 1.4'),
        # (2, 'Bootstrap 3'),
    )
    page_type_choices = (
        # ('job_listing', 'Job Listing Page'),
        ('login', 'Login Page'),
    )
    page_status_choices = (
        ('staging', 'Staging'),
        ('production', 'Production'),
    )

    bootstrap_version = models.PositiveIntegerField(choices=bootstrap_choices,
                                                    default=1)
    page_type = models.CharField(choices=page_type_choices, max_length=255)
    rows = models.ManyToManyField('Row', through='RowOrder')
    site = models.ForeignKey('seo.SeoSite')
    status = models.CharField(choices=page_status_choices, max_length=255,
                              default='production')

    def __unicode__(self):
        return "%s for %s: %s" % (self.page_type, self.site.name, self.pk)

    def all_blocks(self):
        """
        Gets a list of every unique block included in a page.

        """
        query = (models.Q(row__page=self) |
                 models.Q(columnblockorder__column_block__row__page=self))
        return [block.cast() for block in Block.objects.filter(query).distinct()]

    def boostrap_classes(self):
        return "span%s" % ('16' if self.boostrap_version == 1 else '12')

    def render(self, request):
        content = []
        for row in self.rows.all().order_by('roworder__order'):
            content.append(row.render(request))
        return mark_safe(''.join(content))


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
from datetime import datetime, timedelta

from django.contrib.auth.models import ContentType
from django.db import models
from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _


class EmailSection(models.Model):
    SECTION_TYPES = (
        (1, 'Header'),
        (2, 'Body'),
        (3, 'Footer'),
    )

    name = models.CharField(max_length=255)
    owner = models.ForeignKey('seo.Company', blank=True, null=True)
    section_type = models.PositiveIntegerField(choices=SECTION_TYPES)
    content = models.TextField()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.owner or "Global")


class EmailTemplate(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey('seo.Company', blank=True, null=True)
    header = models.ForeignKey('EmailSection', related_name='header_for')
    body = models.ForeignKey('EmailSection', related_name='body_for')
    footer = models.ForeignKey('EmailSection', related_name='footer_for')

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.owner or "Global")

    @staticmethod
    def build_context(for_object):
        """
        Builds context based on a generic number of things that
        a user might want to include in an email.

        :param for_object: The object the context is being built for.
        :return: A dictionary of context for the templates to use.

        """
        context = {}
        # TODO: Build context based on object passed to the function.
        return Context(context)

    def render(self, for_object):
        """
        Renders the EmailTemplate for a given object.

        :param for_object: The object the email is being rendered for.
        :return: The rendered email.
        """
        context = self.build_context(for_object)
        template = Template('\n'.join([self.header.content, self.body.content,
                                       self.footer.content]))
        return template.render(context)


class Event(models.Model):
    email_template = models.ForeignKey('EmailTemplate')
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey('seo.Company')
    sites = models.ManyToManyField('seo.SeoSite')
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.owner)

    class Meta:
        abstract = True

    def send_email(self, for_object):
        """
        Sends an email for a for_object.

        :param for_object: The object an email is being sent for.

        """
        email_content = self.email_template.render(for_object)
        # TODO: Write actual send email logic


class CronEvent(Event):
    model = models.ForeignKey(ContentType,
                              limit_choices_to={'model__in': [
                                  'purchasedjob',
                                  'purchasedproduct']})
    field = models.CharField(max_length=255, blank=True)
    minutes = models.PositiveIntegerField()

    def schedule_task(self, for_object):
        """
        Creates an EmailCronTask for the for_object.

        :param for_object: The object that will have an email sent for it
                           in the future.
        :return: The created EamilCronTask.
        """

        return EmailCronTask.objects.create(
            object_id=for_object.pk,
            model=ContentType.objects.get_for_model(for_object._meta.model),
            related_event=self,
            scheduled_for=self.scheduled_for(for_object),
        )

    def scheduled_for(self, for_object):
        """
        :return: The next valid time this Event would be scheduled for.

        """
        base_time = getattr(for_object, self.field, datetime.now())
        if base_time is None or base_time == '':
            base_time = datetime.now()
        return base_time + timedelta(minutes=self.minutes)


class ValueEvent(Event):
    COMPARISON_CHOICES = (
        ('', 'is equal to'),
        ('__gte', 'is greater than or equal to'),
        ('__lte', 'is less than or equal to'),
    )

    compare_using = models.CharField(_('Comparison Type'),
                                     max_length=255, choices=COMPARISON_CHOICES)
    model = models.ForeignKey(ContentType,
                              limit_choices_to={'model__in': [
                                  'purchasedjob',
                                  'purchasedproduct',
                                  'request']})
    field = models.CharField(max_length=255)
    value = models.PositiveIntegerField()


class EmailCronTask(models.Model):
    object_id = models.PositiveIntegerField()
    model = models.ForeignKey(ContentType)

    completed_on = models.DateTimeField(blank=True, null=True)
    related_event = models.ForeignKey('CronEvent')
    scheduled_for = models.DateTimeField()
    scheduled_at = models.DateTimeField(auto_now_add=True)
from celery.task import task
from datetime import datetime, timedelta
import operator

from django.contrib.auth.models import ContentType, Group
from django.contrib.contenttypes.generic import GenericForeignKey
from django.core.mail import send_mail
from django.db import models, OperationalError
from django.db.models.signals import pre_save, post_save
from django.template import Template, Context
from django.utils.translation import ugettext_lazy as _
from seo.models import CompanyUser


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

    def schedule_task(self, for_object):
        return EmailTask.objects.create(
            act_on=for_object,
            related_event=self,
            scheduled_for=self.schedule_for(for_object)
        )

    def schedule_for(self, for_object):
        return datetime.now()

    def send_email(self, for_object):
        """
        Sends an email for a for_object.

        :param for_object: The object an email is being sent for.
        """
        group, _ = Group.objects.get_or_create(name=self.ADMIN_GROUP_NAME)
        if self.model.model == 'purchasedjob':
            # host company to purchaser
            recipient_company = for_object.owner
            sending_company = for_object.purchased_product.product.owner
        elif self.model.model == 'purchasedproduct':
            # host company to purchaser
            recipient_company = for_object.owner
            sending_company = for_object.product.owner
        elif self.model.model == 'request':
            # purchaser to host company
            recipient_company = for_object.owner
            sending_company = for_object.requesting_company()
        else:  # self.model.model == 'invoice':
            # host company to purchaser
            recipient_company = for_object.purchasedproduct_set.first()\
                .product.owner
            sending_company = for_object.owner

        recipients = CompanyUser.objects.filter(
            company=recipient_company, group=group).values_list('user__email',
                                                                flat=True)
        if hasattr(sending_company, 'companyprofile'):
            email_domain = sending_company.companyprofile.outgoing_email_domain
        else:
            email_domain = 'my.jobs'

        body = self.email_template.render(for_object)
        send_mail('An update on your %s' % self.model.name,
                  body,
                  '%s@%s' % (self.model.model, email_domain),
                  recipients)


CRON_EVENT_MODELS = ['purchasedjob', 'purchasedproduct']
VALUE_EVENT_MODELS = ['purchasedjob', 'purchasedproduct', 'request']
CREATED_EVENT_MODELS = ['invoice']
ALL_EVENT_MODELS = set().union(CRON_EVENT_MODELS, VALUE_EVENT_MODELS,
                               CREATED_EVENT_MODELS)


class CronEvent(Event):
    model = models.ForeignKey(ContentType,
                              limit_choices_to={'model__in': [
                                  'purchasedjob',
                                  'purchasedproduct']})
    field = models.CharField(max_length=255, blank=True)
    minutes = models.IntegerField()

    def schedule_task(self, for_object):
        """
        Creates an EmailCronTask for the for_object.

        :param for_object: The object that will have an email sent for it
                           in the future.
        :return: The created EamilCronTask.
        """
        return EmailTask.objects.create(
            act_on=for_object,
            related_event=self,
            scheduled_for=self.schedule_for(for_object)
        )

    def schedule_for(self, for_object):
        """
        :return: The next valid time this Event would be scheduled for.

        """
        base_time = getattr(for_object, self.field, datetime.now())
        if base_time is None or base_time == '':
            base_time = datetime.now()
        return base_time + timedelta(minutes=self.minutes)


class ValueEvent(Event):
    COMPARISON_CHOICES = (
        ('eq', 'is equal to'),
        ('ge', 'is greater than or equal to'),
        ('le', 'is less than or equal to'),
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


class CreatedEvent(Event):
    model = models.ForeignKey(ContentType,
                              limit_choices_to={'model__in': [
                                  'invoice'
                              ]})


class EmailTask(models.Model):
    # Object being used to generate this email
    object_id = models.PositiveIntegerField()
    object_model = models.ForeignKey(ContentType, related_name='email_model')
    act_on = GenericForeignKey('object_model', 'object_id')

    # Event type of this email
    event_id = models.PositiveIntegerField()
    event_model = models.ForeignKey(ContentType, related_name='email_type')
    related_event = GenericForeignKey('event_model', 'event_id')

    completed_on = models.DateTimeField(blank=True, null=True)

    scheduled_for = models.DateTimeField(default=datetime.now)
    scheduled_at = models.DateTimeField(auto_now_add=True)

    task_id = models.CharField(max_length=36, blank=True, default='',
                               help_text='guid with dashes')

    @property
    def completed(self):
        return bool(self.completed_on)

    def schedule(self):
        send_event_email.apply_async(args=[self], eta=self.scheduled_for)

    def send_email(self):
        self.related_event.send_email(self.act_on)


# I don't really like doing it this way (get from database pre save, set
# attribute, get again post save), but we need to be able to 1) determine what
# was changed and 2) only send an email if the save is successful. - TP
def cron_post_save(sender, instance, **kwargs):
    cron_event_kwargs = {'model': sender,
                         'owner': instance.product.owner if hasattr(
                             instance, 'product') else instance.owner}
    events = [CronEvent.objects.filter(**cron_event_kwargs)]
    tasks = EmailTask.objects.filter(
        object_id=instance.pk,
        object_model=ContentType.objects.get_for_model(instance))
    triggered_events = {task_.related_event for task_ in tasks}
    for event in triggered_events:
        if event in events:
            events.pop(events.index(event))


def value_pre_save(sender, instance, **kwargs):
    triggered = []
    if instance.pk:
        value_event_kwargs = {'model': sender,
                              'owner': instance.product.owner if hasattr(
                                  instance, 'product') else instance.owner}
        events = ValueEvent.objects.filter(**value_event_kwargs)
        original = sender.objects.get(pk=instance.pk)
        for event in events:
            old_val = getattr(original, event.field)
            new_val = getattr(instance, event.field)
            if getattr(operator, event.compare_using, 'eq')(old_val, new_val):
                triggered.append(event.pk)
    instance.triggered = triggered


def value_post_save(sender, instance, **kwargs):
    if instance.triggered:
        events = ValueEvent.objects.filter(id__in=instance.triggered)
        for event in events:
            EmailTask.objects.create(act_on=instance,
                                     related_event=event).schedule()


def created_pre_save(sender, instance, **kwargs):
    # set parameter on instance preserving changed fields
    instance.pre_existing = bool(instance.pk)


def created_post_save(sender, instance, **kwargs):
    if not instance.pre_existing:
        # This is a new instance. Determine if the owning company has the
        # proper items in place to allow for email sending.
        content_type = ContentType.objects.get_for_model(sender)
        events = CreatedEvent.objects.filter(model=content_type,
                                             owner=instance.owner)
        for event in events:
            # Company has events for this model. Schedule an email.
            EmailTask.objects.create(act_on=instance,
                                     related_event=event).schedule()


bind_events = lambda pre=None, post=None: [
    pre_save.connect(pre, sender=ct.model_class(),
                     dispatch_uid='pre_save__%s' % model) if pre else None,
    post_save.connect(post, sender=ct.model_class(),
                      dispatch_uid='pre_save__%s' % model) if post else None]
try:
    for model in ALL_EVENT_MODELS:
        ct = ContentType.objects.get(model=model)
        if model in CRON_EVENT_MODELS:
            bind_events(post=cron_post_save)
        if model in VALUE_EVENT_MODELS:
            bind_events(value_pre_save, value_post_save)
        if model in CREATED_EVENT_MODELS:
            bind_events(created_pre_save, created_post_save)
except OperationalError:
    # We're running syncdb and the ContentType table doesn't exist yet
    pass


@task(name="tasks.send_event_email", ignore_result=True)
def send_event_email(email_task):
    """
    Send an appropriate email given an EmailTask instance.

    :param email_task: EmailTask we are using to generate this email
    """
    email_task.task_id = send_event_email.request.id
    email_task.save()

    email_task.send_email()

    email_task.completed_on = datetime.now()
    email_task.save()

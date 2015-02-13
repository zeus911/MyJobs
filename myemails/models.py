from django.contrib.auth.models import ContentType
from django.db import models


class EmailTemplate(models.Model):
    # header = models.ForeignKey()
    # footers = models.ForeignKey()

    pass


class Event(models.Model):
    COMPARISON_CHOICES = (
        ('', 'is equal to'),
        ('__gte', 'is greater than or equal to'),
        ('__lte', 'is less than or equal to'),
    )
    email_template = models.ForeignKey('EmailTemplate', null=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey('seo.Company')

    compare_using = models.CharField(choices=COMPARISON_CHOICES)
    model = models.ForeignKey(ContentType)
    field = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def send_email(self, for_object):
        pass


class CronEvent(Event):
    value = models.TimeField()

    def schedule_task(self, for_object):
        EmailCronTask.objects.create(
            object_id=for_object.pk,
            model=ContentType.objects.get_for_model(for_object._meta.model),
            related_event=self,
            scheduled_for=self.scheduled_for(for_object),
        )

    def scheduled_for(self, for_object):
        """
        :return: The next valid time this Event would be scheduled for.

        """
        
        return None


class ValueEvent(Event):
    value = models.PositiveIntegerField()


class EmailCronTask(models.Model):
    object_id = models.PositiveIntegerField()
    model = models.ForeignKey(ContentType)

    completed_on = models.DateTimeField(blank=True, null=True)
    related_event = models.ForeignKey('EmailCron')
    scheduled_for = models.DateTimeField()
    scheduled_at = models.DateTimeField(auto_now_add=True)
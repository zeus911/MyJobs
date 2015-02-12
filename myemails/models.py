from django.contrib.auth.models import ContentType
from django.db import models


class EmailTemplate(models.Model):
    pass


class Event(models.Model):
    email_template = models.ForeignKey('EmailTemplate', null=True)
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey('seo.Company')

    class Meta:
        abstract = True

    def send_email(self):
        return


class ActionEvent(Event):
    pass


class CronEvent(Event):
    pass

    def schedule_task(self):
        pass


class ValueEvent(Event):
    trigger_model = models.ForeignKey(ContentType)
    trigger_field = models.CharField(max_length=255)
    trigger_value = models.PositiveIntegerField()

    def is_triggered(self, obj):
        actual_value = getattr(obj, self.trigger_field, None)
        return actual_value == self.trigger_value


class EmailCronTask(models.Model):
    completed_on = models.DateTimeField(blank=True, null=True)
    related_event = models.ForeignKey('EmailCron')
    scheduled_for = models.DateTimeField()
    scheduled_at = models.DateTimeField(auto_now_add=True)

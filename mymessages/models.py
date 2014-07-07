import collections
import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group

from myjobs.models import User


def start_default():
    return datetime.datetime.now()


def expire_default():
    return datetime.datetime.now() + datetime.timedelta(days=14)


class MessageManager(models.Manager):
    def create_message(self, subject, body, expires=True, **kwargs):
        """
        Create a message for one or more users.
        If users is provided but not groups, just those users will receive
        the message. If groups is provided but not users, all members of that
        group, past, current, and future, should see it. If both are provided,
        all group members as well as the specified users (even if they are not
        group members) will get the message.

        Inputs:
        :subject: Subject title for message being created
        :body: Body text of the message to be created
        :expires: Will this message have an expiration date, default: True
        :users: List of users to add this message to; :users:, :groups:, or
            both must be provided
        :groups: List of groups whose members should see this message; :users:,
            :groups:, or both must be provided
        :kwargs: Other fields from the Message model, all optional
        """
        users = kwargs.pop('users', None)
        if users is not None and not isinstance(users, collections.Iterable):
            users = [users]

        kwargs.setdefault('message_type', 'error')

        if not expires:
            kwargs['expires_at'] = None

        groups = kwargs.pop('groups', None)

        if groups is None and users is None:
            raise ValueError("users and/or groups must have a value")

        message = self.create(subject=subject, body=body, **kwargs)

        if groups is not None:
            if not isinstance(groups, collections.Iterable):
                groups = [groups]
            for group in groups:
                message.group.add(group)

        if users is not None:
            for user in users:
                MessageInfo.objects.create(user=user, message=message)

        return message


class Message(models.Model):
    """
    Message
    """
    TYPE_OF_MESSAGES = (
        ('error', 'Error'),
        ('info', 'Info'),
        ('block', 'Notice'),
        ('success', 'Success'),
    )
    group = models.ManyToManyField(Group)
    users = models.ManyToManyField(User, through='MessageInfo')
    subject = models.CharField("Subject", max_length=200)
    message_type = models.CharField("Type of message", choices=TYPE_OF_MESSAGES,
                                    max_length=200)
    body = models.TextField('Body')
    start_on = models.DateTimeField('start on', default=start_default)
    expire_at = models.DateTimeField('expire at',
                                     default=expire_default,
                                     null=True,
                                     help_text="Default is two weeks " +
                                               "after message is sent.")
    btn_text = models.CharField('Button Text', max_length=100, default='Okay')

    objects = MessageManager()

    def __unicode__(self):
        return self.subject


class MessageInfo(models.Model):
    """
    Through model for Message.
    """
    user = models.ForeignKey(User)
    message = models.ForeignKey(Message)
    read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField('read at', null=True)
    expired = models.BooleanField(default=False, db_index=True)
    expired_on = models.DateTimeField('expired on', null=True)

    def __unicode__(self):
        return self.message.subject

    def is_unread(self):
        return bool(self.read_at is None)

    def mark_unread(self):
        self.read = False
        self.read_at = None
        self.save()

    def mark_read(self):
        self.read = True
        self.read_at = datetime.datetime.now()
        self.save()

    def mark_expired(self):
        self.read = False
        self.expired = True
        self.expired_on = datetime.datetime.now()
        self.save()

    def expired_time(self):
        message = self.message
        if message.expire_at is None:
            return False
        now = timezone.now()
        if timezone.is_naive(self.message.expire_at):
            message.expire_at = timezone.make_aware(
                message.expire_at, timezone.UTC())
        if timezone.is_naive(self.message.start_on):
            message.start_on = timezone.make_aware(
                message.start_on, timezone.UTC())
        date_expired = (message.expire_at - message.start_on) + \
                       message.start_on
        if now > date_expired:
            self.mark_expired()
            return True
        else:
            return False


def get_messages(user):
    """
    Gathers Messages based on user's groups and if message has started and is
    not expired.

    Inputs:
    :user:              User obj to get user's groups

    Outputs:
    :active_messages:   A list of messages that starts before the current
                        time and expires after the current time. 'active'
                        messages.
    """
    now = timezone.now()
    groups = Group.objects.filter(user=user)
    messages = set(Message.objects.filter(group__in=groups, start_on__lte=now,
                                          expire_at__gt=now)).union(
                   set(Message.objects.filter(users=user)))
    return messages
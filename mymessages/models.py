import collections
import datetime

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import Group


def start_default():
    return datetime.datetime.now()


def expire_default():
    return datetime.datetime.now() + datetime.timedelta(days=14)


class MessageManager(models.Manager):
    def create_message(self, subject, body, users=None, groups=None,
                       expires=True, **kwargs):
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
        :users: List of users to add this message to; :users:, :groups:, or
            both must be provided
        :groups: List of groups whose members should see this message; :users:,
            :groups:, or both must be provided
        :expires: Will this message have an expiration date, default: True
        :kwargs: Other fields from the Message model, all optional
        """
        kwargs.setdefault('message_type', 'error')

        if not expires:
            # Message should not expire; ensure expire_at is not going to be
            # set by the caller
            kwargs['expire_at'] = None

        if groups is None and users is None:
            raise ValueError("users and/or groups must have a value")

        message = self.create(subject=subject, body=body, **kwargs)

        if groups is not None:
            if not isinstance(groups, collections.Iterable):
                groups = [groups]
            for group in groups:
                message.group.add(group)

        if users is not None:
            # Users are associated with messages via the MessageInfo through
            # table. If we are going to add users, we need to add entries to
            # the through table for them.
            if not isinstance(users, collections.Iterable):
                users = [users]

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
    ACCOUNT = 'account'
    PRM = 'prm'
    MESSAGE_CLASSES = [ACCOUNT, PRM]
    MESSAGE_CLASS_CHOICES = zip(MESSAGE_CLASSES, ['Account', 'PRM'])
    group = models.ManyToManyField(Group)
    users = models.ManyToManyField('myjobs.User', through='MessageInfo')
    subject = models.CharField("Subject", max_length=200)
    message_type = models.CharField("Message type", choices=TYPE_OF_MESSAGES,
                                    max_length=200)
    body = models.TextField('Body')
    start_on = models.DateTimeField('Start on', default=start_default)
    expire_at = models.DateTimeField('Expire at',
                                     default=expire_default,
                                     null=True,
                                     help_text="Default is two weeks " +
                                               "after message is sent.")
    btn_text = models.CharField('Button text', max_length=100, default='OK')
    message_class = models.CharField('Message class',
                                     choices=MESSAGE_CLASS_CHOICES,
                                     max_length=200, default=ACCOUNT)

    objects = MessageManager()

    def __unicode__(self):
        return self.subject


class MessageInfo(models.Model):
    """
    Through model for Message.
    """
    user = models.ForeignKey('myjobs.User')
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


def get_messages(user, limit_to=None):
    """
    Gathers Messages based on user, user's groups and if message has started
    and is not expired.

    Inputs:
    :user:              User obj to get user's groups
    :limit_to:          Limits returned messages to a given message class;
                        Default: no limit

    Outputs:
    :active_messages:   A list of messages that starts before the current
                        time and expires after the current time. 'active'
                        messages.
    """
    assert limit_to in Message.MESSAGE_CLASSES + [None], 'limit_to is ' +\
        'invalid; got %s, expected one of %s' % (limit_to,
                                                 Message.MESSAGE_CLASSES + [None])
    now = timezone.now().date()
    messages = Message.objects.prefetch_related('messageinfo_set').filter(
        Q(group__in=user.groups.all()) | Q(users=user),
        Q(expire_at__isnull=True) | Q(expire_at__gte=now))
    if limit_to is not None:
        messages = messages.filter(message_class=limit_to)
    messages = messages.distinct()

    return messages

from os import path
from re import sub
from urllib import urlencode
from uuid import uuid4

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.db import models

from myjobs.models import User
from mydashboard.models import Company


CONTACT_TYPE_CHOICES = (('email', 'Email'),
                        ('phone', 'Phone'),
                        ('facetoface', 'Face to Face'),
                        ('job', 'Job Followup'),
                        ('pssemail', "Partner Saved Search Email"))


# Flags for ContactLogEntry action_flag. Based on django.contrib.admin.models
# action flags.
ADDITION = 1
CHANGE = 2
DELETION = 3
EMAIL = 4

ACTIVITY_TYPES = {
    1: 'added',
    2: 'updated',
    3: 'deleted',
    4: 'sent',
}


class Contact(models.Model):
    """
    Everything here is self explanatory except for one part. With the Contact
    object there is Contact.partner_set and .partners_set

    """
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    partner = models.ForeignKey('Partner')
    name = models.CharField(max_length=255, verbose_name='Full Name')
    email = models.EmailField(max_length=255, verbose_name='Email', blank=True)
    phone = models.CharField(max_length=30, verbose_name='Phone', blank=True)
    label = models.CharField(max_length=60, verbose_name='Address Label',
                             blank=True)
    address_line_one = models.CharField(max_length=255,
                                        verbose_name='Address Line One',
                                        blank=True)
    address_line_two = models.CharField(max_length=255,
                                        verbose_name='Address Line Two',
                                        blank=True)
    city = models.CharField(max_length=255, verbose_name='City', blank=True)
    state = models.CharField(max_length=5, verbose_name='State/Region',
                             blank=True)
    country_code = models.CharField(max_length=3, verbose_name='Country',
                                    blank=True)
    postal_code = models.CharField(max_length=12, verbose_name='Postal Code',
                                   blank=True)
    notes = models.TextField(max_length=1000, verbose_name='Notes', blank=True)

    class Meta:
        verbose_name_plural = 'contacts'

    def __unicode__(self):
        if self.name:
            return self.name
        if self.email:
            return self.email
        return 'Contact object'

    def save(self, *args, **kwargs):
        """
        Checks to see if there is a User that is using self.email add said User
        to self.user

        """
        if not self.user:
            if self.email:
                try:
                    user = User.objects.get(email=self.email)
                except User.DoesNotExist:
                    pass
                else:
                    self.user = user
        return super(Contact, self).save(*args, **kwargs)

    def get_contact_url(self):
        base_urls = {
            'contact': reverse('edit_contact'),
        }
        params = {
            'partner': self.partner.pk,
            'company': self.partner.owner.pk,
            'id': self.pk,
            'ct': ContentType.objects.get_for_model(Contact).pk
        }
        query_string = urlencode(params)
        return "%s?%s" % (base_urls[self.content_type.name], query_string)

class Partner(models.Model):
    """
    Object that this whole app is built around.

    """
    name = models.CharField(max_length=255,
                            verbose_name='Partner Organization')
    uri = models.URLField(verbose_name='Partner URL', blank=True)
    primary_contact = models.ForeignKey('Contact', null=True,
                                        related_name='primary_contact',
                                        on_delete=models.SET_NULL)
    # owner is the Company that owns this partner.
    owner = models.ForeignKey(Company)

    def __unicode__(self):
        return self.name


class ContactRecord(models.Model):
    """
    Object for Communication Records
    """

    created_on = models.DateTimeField(auto_now=True)
    partner = models.ForeignKey(Partner)
    contact_type = models.CharField(choices=CONTACT_TYPE_CHOICES,
                                    max_length=12,
                                    verbose_name="Contact Type")
    contact_name = models.CharField(max_length=255, verbose_name='Contacts',
                                    blank=True)
    # contact type fields, fields required depending on contact_type. Enforced
    # on the form level.
    contact_email = models.CharField(max_length=255,
                                     verbose_name="Contact Email",
                                     blank=True)
    contact_phone = models.CharField(verbose_name="Contact Phone Number",
                                     max_length=30, blank=True)
    location = models.CharField(verbose_name="Meeting Location", max_length=255,
                                blank=True)
    length = models.TimeField(verbose_name="Meeting Length", blank=True,
                              null=True)
    subject = models.CharField(verbose_name="Subject or Topic", max_length=255,
                               blank=True)
    date_time = models.DateTimeField(verbose_name="Date & Time", blank=True)
    notes = models.TextField(max_length=1000,
                             verbose_name='Details, Notes or Transcripts',
                             blank=True)
    job_id = models.CharField(max_length=40, verbose_name='Job Number/ID',
                             blank=True)
    job_applications = models.CharField(max_length=6,
                                        verbose_name="Number of Applications",
                                        blank=True)
    job_interviews = models.CharField(max_length=6,
                                      verbose_name="Number of Interviews",
                                      blank=True)
    job_hires = models.CharField(max_length=6, verbose_name="Number of Hires",
                                 blank=True)

    def __unicode__(self):
        return "%s Contact Record - %s" % (self.contact_type, self.subject)

    def get_record_description(self):
        """
        Generates a human readable description of the contact
        record.

        """
        contact_type = dict(CONTACT_TYPE_CHOICES)[self.contact_type]
        if contact_type == 'Email':
            contact_type = 'n email'
        else:
            contact_type = ' %s' % contact_type

        try:
            logs = ContactLogEntry.objects.filter(object_id=self.pk)
            log = logs.order_by('-action_time')[:1][0]
        except IndexError:
            return ""

        contact_str = "A%s record for %s was %s" % \
                      (contact_type.lower(),
                       self.contact_name, ACTIVITY_TYPES[log.action_flag])

        if log.user:
            user = log.user.get_full_name() if log.user.get_full_name() else \
                log.user.email
            contact_str = "%s by %s" % (contact_str, user)

        return contact_str

    def get_record_url(self):
        params = {
            'partner': self.partner.pk,
            'company': self.partner.owner.pk,
            'id': self.pk,
        }
        query_string = urlencode(params)
        return "%s?%s" % (reverse('record_view'), query_string)

MAX_ATTACHMENT_MB = 4


class PRMAttachment(models.Model):

    def get_file_name(self, filename):
        """
        Ensures that a file name is unique before uploading.
        The PRMAttachment instance requires an extra attribute,
        partner (a Partner instance) to be set in order to create the
        file name.

        """
        filename, extension = path.splitext(filename)
        filename = '.'.join([sub(r'[\W]', '', filename),
                             sub(r'[\W]', '', extension)])
        uid = uuid4()
        path_addon = "mypartners/%s/%s/%s" % (self.partner.owner.pk,
                                              self.partner.pk, uid)
        name = "%s/%s" % (path_addon, filename)

        # Make sure that in the unlikely event that a filepath/uid/filename
        # combination isn't actually unique a new unique id
        # is generated.
        while default_storage.exists(name):
            uid = uuid4()
            path_addon = "mypartners/%s/%s/%s" % (self.partner.owner,
                                                  self.partner.name, uid)
            name = "%s/%s" % (path_addon, filename)
        return name

    attachment = models.FileField(upload_to=get_file_name, blank=True,
                                  null=True, max_length=767)
    contact_record = models.ForeignKey(ContactRecord, null=True,
                                       on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        instance = super(PRMAttachment, self).save(*args, **kwargs)

        # Confirm that we're not trying to change public/private status of
        # actual files during local testing.
        try:
            if repr(default_storage.connection) == 'S3Connection:s3.amazonaws.com':
                from boto import connect_s3, s3
                conn = connect_s3(settings.AWS_ACCESS_KEY_ID,
                                  settings.AWS_SECRET_KEY)
                bucket = conn.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
                key = s3.key.Key(bucket)
                key.key = self.attachment.name
                key.set_acl('private')
        except AttributeError:
            pass

        return instance

    def delete(self, *args, **kwargs):
        filename = self.attachment.name
        super(PRMAttachment, self).delete(*args, **kwargs)
        default_storage.delete(filename)


class ContactLogEntry(models.Model):
    action_flag = models.PositiveSmallIntegerField('action flag')
    action_time = models.DateTimeField('action time', auto_now=True)
    change_message = models.TextField('change message', blank=True)
    # A value that can meaningfully (email, name) identify the contact.
    contact_identifier = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.TextField('object id', blank=True, null=True)
    object_repr = models.CharField('object repr', max_length=200)
    partner = models.ForeignKey(Partner, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def get_edited_object(self):
        """
        Returns the edited object represented by this log entry

        """
        try:
            return self.content_type.get_object_for_this_type(pk=self.object_id)
        except self.content_type.model_class().DoesNotExist:
            return None

    def get_object_url(self):
        """
        Creates the link that leads to the view/edit view for that object.

        """
        obj = self.get_edited_object()
        if not obj or not self.partner:
            return None
        base_urls = {
            'contact': reverse('edit_contact'),
            'contact record': reverse('record_view'),
            'partner saved search': reverse('partner_edit_search'),
            'partner': reverse('create_partner'),
        }
        params = {
            'partner': self.partner.pk,
            'company': self.partner.owner.pk,
            'id': obj.pk,
            'ct': self.content_type.pk,
        }
        query_string = urlencode(params)
        return "%s?%s" % (base_urls[self.content_type.name], query_string)
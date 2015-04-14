import hmac
from hashlib import sha1
import uuid

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, **kwargs):
        """
        Creates an already activated user.

        """
        email = kwargs['email']
        password = kwargs['password1']
        if not email:
            raise ValueError('Email address required.')
        user = self.model(email=CustomUserManager.normalize_email(email))
        user.is_active = True
        user.gravatar = 'none'
        user.set_password(password)
        user.save(using=self._db)
        user.make_guid()
        return user

    def create_superuser(self, **kwargs):
        email = kwargs['email']
        password = kwargs['password']
        if not email:
            raise ValueError('Email address required.')
        u = self.model(email=CustomUserManager.normalize_email(email))
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.gravatar = u.email
        u.set_password(password)
        u.save(using=self._db)
        u.make_guid()
        return u


class User(AbstractBaseUser, PermissionsMixin):
    """
    This is a minimal version of the myjobs user.

    """
    class Meta:
        db_table = 'myjobs_user'

    email = models.EmailField(max_length=255, unique=True, db_index=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Permission Levels
    is_staff = models.BooleanField('staff status', default=False)
    is_active = models.BooleanField('active', default=True)
    is_disabled = models.BooleanField('disabled', default=False)

    user_guid = models.CharField(max_length=100, db_index=True, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)

    USERNAME_FIELD = 'email'
    objects = CustomUserManager()

    def __unicode__(self):
        return self.email

    def get_username(self):
        return self.email

    def get_short_name(self):
        return self.email

    def disable(self):
        self.is_active = False
        self.is_disabled = True
        self.save()

    def make_guid(self):
        """
        Creates a uuid for the User only if the User does not currently has
        a user_guid.  After the uuid is made it is checked to make sure there
        are no duplicates. If no duplicates, save the GUID.
        """
        if not self.user_guid:
            self.user_guid = uuid.uuid4().hex
            if User.objects.filter(user_guid=self.user_guid):
                self.make_guid()
            self.save()


class APIUser(models.Model):
    class Meta:
        verbose_name = 'API User'

    SCOPE_CHOICES = (('1', 'All'), ('7', 'Network Only'), )

    company = models.CharField(max_length=255, verbose_name="Company")
    key = models.CharField(max_length=255, unique=True)

    first_name = models.CharField(max_length=200, blank=True, default='')
    last_name = models.CharField(max_length=200, blank=True, default='')
    email = models.CharField(max_length=200, blank=True, default='')
    phone = models.CharField(max_length=30,  blank=True, default='')

    scope = models.CharField(max_length=1, choices=SCOPE_CHOICES, default=1)
    jv_api_access = models.BooleanField(default=0, verbose_name='Job View Access')
    onet_access = models.BooleanField(default=0, verbose_name='Onet Access')

    view_source = models.IntegerField('ViewSource', null=True, db_column='view_source_id')
    disable = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_disabled = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.company

    def create_key(self):
        self.key = hmac.new(uuid.uuid4().bytes, digestmod=sha1).hexdigest()
        self.save()

    def save(self, *args, **kwargs):
        if not self.key:
            self.create_key()
        return super(APIUser, self).save(*args, **kwargs)


class ViewSource(models.Model):
    view_source_id = models.IntegerField(primary_key=True, blank=True,
                                         default=None)
    name = models.CharField(max_length=255, blank=True)
    friendly_name = models.CharField(max_length=255, blank=True)

    class Meta:
        get_latest_by = 'view_source_id'
        verbose_name = 'View Source'
        db_table = 'redirect_viewsource'

    def __unicode__(self):
        return u'%s (%d)' % (self.name, self.view_source_id)


class CityToCentroidMapping(models.Model):
    city = models.CharField(max_length=255, db_index=True)
    state = models.CharField(max_length=3, db_index=True)
    centroid_lat = models.CharField(max_length=25)
    centroid_lon = models.CharField(max_length=25)


class ZipCodeToCentroidMapping(models.Model):
    zip_code = models.CharField(max_length=7, unique=True, db_index=True)
    centroid_lat = models.CharField(max_length=25)
    centroid_lon = models.CharField(max_length=25)


class Search(models.Model):
    query = models.TextField()
    solr_params = models.TextField()
    user = models.ForeignKey('APIUser', db_index=True)
    date_last_accessed = models.DateTimeField(auto_now=True, null=True,
                                              db_index=True)


class Onet(models.Model):
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = "Onet"
        verbose_name_plural = "Onets"
        unique_together = ("title", "code")
        db_table = 'moc_coding_onet'

    title = models.CharField(max_length=300)
    code = models.CharField(max_length=10, primary_key=True)


class Moc(models.Model):
    class Meta:
        verbose_name = "Military Occupational Code/Rating"
        verbose_name_plural = "Military Occupational Codes"
        unique_together = ("code", "branch")
        ordering = ['branch', 'code']
        db_table = 'moc_coding_moc'

    code = models.CharField(max_length=20, db_index=True)
    branch = models.CharField(max_length=11)
    title = models.CharField(max_length=300)
    title_slug = models.SlugField(max_length=300)
    onets = models.ManyToManyField(Onet)


class Industry(models.Model):
    industry_id = models.IntegerField(max_length=255, primary_key=True)
    industry = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return "%s %s" % (self.industry, self.industry_id)


class Country(models.Model):
    country_code = models.IntegerField(max_length=255, primary_key=True)
    country = models.CharField(max_length=255, db_index=True)

    def __unicode__(self):
        return self.country

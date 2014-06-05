import datetime
import urllib
import hashlib
import uuid

from django.utils.safestring import mark_safe
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        Group, PermissionsMixin)
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils.importlib import import_module

from default_settings import GRAVATAR_URL_PREFIX, GRAVATAR_URL_DEFAULT
from registration import signals as custom_signals


class CustomUserManager(BaseUserManager):
    def get_email_owner(self, email):
        """
        Tests if the specified email is already in use.

        Inputs:
        :email: String representation of email to be checked

        Outputs:
        :user: User object if one exists; None otherwise
        """
        try:
            user = self.get(email__iexact=email)
        except User.DoesNotExist:
            try:
                user = self.get(
                    profileunits__secondaryemail__email__iexact=email)
            except User.DoesNotExist:
                user = None
        return user

    def create_inactive_user(self, send_email=True, request=None, **kwargs):
        """
        Creates an inactive user, calls the registration app to generate a
        key and sends an activation email to the user.

        Inputs:
        :send_email: Boolean defaulted to true to signal that an email needs to
        be sent.
        :kwargs: Email and password information

        Outputs:
        :user: User object instance
        :created: Boolean indicating whether a new user was created
        """
        email = kwargs.get('email')
        password = kwargs.get('password1')

        user = self.get_email_owner(email)
        created = False
        if user is None:
            email = CustomUserManager.normalize_email(email)
            user = self.model(email=email)
            if password:
                auto_generated = False
            else:
                auto_generated = True
                user.password_change = True
                password = self.make_random_password(length=8)
            user.set_password(password)
            user.is_active = False
            user.gravatar = ''
            user.make_guid()
            user.timezone = settings.TIME_ZONE
            if request is not None:
                source = request.GET.get('source')
                if source is not None:
                    user.source = source
                else:
                    last_microsite = request.COOKIES.get('lastmicrosite', None)
                    if last_microsite is not None:
                        user.source = last_microsite
            user.full_clean()
            user.save(using=self._db)
            user.add_default_group()
            created = True
            custom_signals.email_created.send(sender=self, user=user,
                                              email=email)
            if send_email:
                custom_msg = kwargs.get("custom_msg", None)
                if auto_generated:
                    custom_signals.send_activation.send(sender=self,
                                                        user=user,
                                                        email=email,
                                                        password=password,
                                                        custom_msg=custom_msg)
                else:
                    custom_signals.send_activation.send(sender=self,
                                                        user=user,
                                                        email=email,
                                                        custom_msg=custom_msg)
        return user, created

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
        user.gravatar = ''
        user.set_password(password)
        user.make_guid()
        user.full_clean()
        user.save(using=self._db)
        user.add_default_group()
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
        u.timezone = settings.TIME_ZONE
        u.make_guid()
        u.full_clean()
        u.save(using=self._db)
        u.add_default_group()
        return u

    def not_disabled(self, user):
        """
        Used by the user_passes_test decorator to set view permissions.
        The user_passes_test method, passes in the user from the request,
        and gives permission to access the view if the value returned is true.
        This returns true as long as the user hasn't disabled their account.
        """

        if user.is_anonymous():
            return False
        else:
            return not user.is_disabled

    def is_active(self, user):
        """
        Used by the user_passes_test decorator to set view permissions
        """

        if user.is_anonymous():
            return False
        else:
            return user.is_active

    def is_group_member(self, user, group):
        """
        Used by the user_passes_test decorator to determine if the user's group
        membership is adequate for certain actions

        Example usage:
        Determine if user is in the 'Job Seeker' group:
        @user_passes_test(lambda u: User.objects.is_group_member(u, 'Job Seeker'))

        Inputs:
        :user: User instance, passed by the user_passes_test decorator
        :group: Name of the group that is being tested for

        Outputs:
        :is_member: Boolean representing the user's membership status
        """
        return user.groups.filter(name=group).count() >= 1


# New in Django 1.5. This is now the default auth user table.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name=_("email address"),
                              max_length=255, unique=True, db_index=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    gravatar = models.EmailField(verbose_name=_("gravatar email"),
                                 max_length=255, db_index=True, blank=True)

    profile_completion = models.IntegerField(validators=[MaxValueValidator(100),
                                                         MinValueValidator(0)],
                                             blank=False, default=0)

    # Permission Levels
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_("Designates whether the user "
                                               "can log into this admin site."))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_("Designates whether this user "
                                                "should be treated as active. "
                                                "Unselect this instead of "
                                                "deleting accounts."))
    is_disabled = models.BooleanField(_('disabled'), default=False)

    # Communication Settings

    # opt_in_myjobs is current hidden on the top level, refer to forms.py
    opt_in_myjobs = models.BooleanField(_('Opt-in to non-account emails and '
                                          'Saved Search'),
                                        default=True,
                                        help_text=_('Checking this enables '
                                                    'my.jobs to send email '
                                                    'updates to you.'))

    opt_in_employers = models.BooleanField(_('Email is visible to Employers'),
                                           default=True,
                                           help_text=_("Employers can "
                                                       "message me."))
    
    last_response = models.DateField(default=datetime.datetime.now, blank=True)

    # Password Settings
    password_change = models.BooleanField(_('Password must be changed on next '
                                            'login'), default=False)

    user_guid = models.CharField(max_length=100, db_index=True, unique=True)

    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=255, default=settings.TIME_ZONE)

    source = models.CharField(max_length=255,
                              default='https://secure.my.jobs',
                              help_text=_('Site that initiated account '
                                          'creation'))

    USERNAME_FIELD = 'email'
    objects = CustomUserManager()

    def __unicode__(self):
        return self.email

    def email_user(self, subject, message, from_email):
        msg = EmailMessage(subject, message, from_email, [self.email])
        msg.content_subtype = 'html'
        msg.send()

    def get_username(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_gravatar_url(self, size=20):
        """
        Gets the container for the gravatar/initials block.

        inputs:
        :self: A user.
        :size: The height and width the resulting block should be.

        outputs:
        :gravatar_url: Either an image tag with a src = to a valid gravatar, or
                       a div tag for the initials block.
        """

        gravatar_url = GRAVATAR_URL_PREFIX + \
            hashlib.md5(self.gravatar.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d': GRAVATAR_URL_DEFAULT,
                                          's': str(size)})
        
        if urllib.urlopen(gravatar_url).getcode() == 404:
            # Determine background color for initials block based on the
            # same formula used for profile completion bars.
            from helpers import get_completion

            color = get_completion(self.profile_completion)

            try:
                text = self.profileunits_set.get(content_type__name="name",
                                                 name__primary=True).name
                if not text.given_name and not text.family_name:
                    text = self.email[0]
                else:
                    text = "%s%s" % (text.given_name[0], text.family_name[0])
            except ObjectDoesNotExist:
                text = self.email[0]

            font_size = int(size)
            font_size *= .65
            gravatar_url = mark_safe(
                "<div class='gravatar-blank gravatar-%s' style='height: %spx; "
                "width: %spx'><span class='gravatar-text' style='font-size:"
                "%spx;'>%s</span></div>" % (color, size, size,
                                            font_size, text.upper()))
        else:
            gravatar_url = mark_safe("<img src='%s' id='id_gravatar'>"
                                     % gravatar_url)

        return gravatar_url

    def disable(self):
        self.is_active = False
        self.is_disabled = True
        self.save()
        
        custom_signals.user_disabled.send(sender=self, user=self,
                                          email=self.email)

    def update_profile_completion(self):
        """
        Updates the percent of modules in
        settings.PROFILE_COMPLETION_MODULES that a user has completed.
        """
        profile_dict = self.profileunits_set.all()        
        num_complete = len(list(set([unit.get_model_name() for unit
                           in profile_dict if unit.get_model_name()
                           in settings.PROFILE_COMPLETION_MODULES])))
        self.profile_completion = int(float(
            1.0 * num_complete / len(settings.PROFILE_COMPLETION_MODULES))*100)
        self.save()

    def add_default_group(self):
        group = Group.objects.get(name='Job Seeker')
        self.groups.add(group.pk)

    def make_guid(self):
        """
        Creates a uuid for the User only if the User does not currently has
        a user_guid.  After the uuid is made it is checked to make sure there
        are no duplicates. If no duplicates, save the GUID.
        """
        if not self.user_guid:
            guid = uuid.uuid4().hex
            if User.objects.filter(user_guid=guid):
                self.make_guid()
            else:
                self.user_guid = guid

    def messages_unread(self):
        """
        Gets a list of active Messages from get_messages. Then gets or creates
        MessageInfo based on user a Message. If the MessageInfo has been read
        already or is expired, ignore it, otherwise add it to 'message_infos'.

        Output:
        :message_infos:  A list of Messages to be shown to the User.
        """
        from mymessages.models import get_messages, MessageInfo
        messages = get_messages(self)
        message_infos = []
        for message in messages:
            m, created = MessageInfo.objects.get_or_create(user=self,
                                                           message=message)
            if not created:
                if m.read or m.expired_time():
                    continue
                else:
                    message_infos.append(m)
            else:
                message_infos.append(m)
        return message_infos

    def get_full_name(self, default=""):
        """
        Returns the user's full name based off of first_name and last_name
        from the user model.

        Inputs:
        :default:   Can add a default if the user doesn't have a first_name
                    or last_name.
        """
        if self.first_name and self.last_name:
            return "%s %s" % (self.first_name, self.last_name)
        else:
            return default

    def add_primary_name(self, update=False, f_name="", l_name=""):
        """
        Primary function that adds the primary user's ProfileUnit.Name object
        first and last name to the user model, if Name object exists.

        Inputs:
        :update:    Update is a flag that should be used to determine if to use
                    this function as an update (must provide f_name and l_name
                    if that is the case) or if the function needs to be called
                    to set the user's first_name and last_name in the model.

        :f_name:    If the update flag is set to true this needs to have the
                    given_name value from the updating Name object.

        :l_name:    If the update flag is set to true this needs to have the
                    family_name value from the updating Name object.
        """
        if update and f_name != '' and l_name != '':
            self.first_name = f_name
            self.last_name = l_name
            self.save()
            return

        try:
            name_obj = self.profileunits_set.filter(
                content_type__name="name").get(name__primary=True)
        except ObjectDoesNotExist:
            name_obj = None

        if name_obj:
            self.first_name = name_obj.name.given_name
            self.last_name = name_obj.name.family_name
            self.save()
        else:
            self.first_name = ""
            self.last_name = ""
            self.save()


class EmailLog(models.Model):
    email = models.EmailField(max_length=254)
    event = models.CharField(max_length=11)
    received = models.DateField()
    processed = models.BooleanField(default=False, blank=True)


class CustomHomepage(Site):
    logo_url = models.URLField('Logo Image URL', max_length=200, null=True,
                               blank=True)
    show_signup_form = models.BooleanField(default=True)


class Ticket(models.Model):
    class Meta:
        unique_together = ['ticket', 'user']

    ticket = models.CharField(max_length=255)
    user = models.ForeignKey('User')


class Shared_Sessions(models.Model):
    # mj_session and ms_session are comma separated list stored as a string
    # of session keys
    mj_session = models.TextField(blank=True)
    ms_session = models.TextField(blank=True)
    user = models.ForeignKey('User', unique=True)


def save_related_session(sender, user, request, **kwargs):
    if user and user.is_authenticated():
        session, _ = Shared_Sessions.objects.get_or_create(user=user)
        current = session.mj_session.split(",") if session.mj_session else []
        try:
            current.append(request.session.session_key)
            session.mj_session = ",".join(current)
        except:
            pass
        session.save()


def delete_related_session(sender, user, request, **kwargs):
    """
    Deletes all microsites sessions for user on logout.

    """

    if user and user.is_authenticated():
        try:
            sessions = Shared_Sessions.objects.get(user=user)
        except Shared_Sessions.DoesNotExist:
            return

        ms_sessions = sessions.ms_session.split(",") if \
            sessions.ms_session else []
        engine = import_module(settings.SESSION_ENGINE)
        for ms_session in ms_sessions:
            try:
                s = engine.SessionStore(ms_session)
                s.delete()
            except:
                pass
        sessions.delete()

user_logged_in.connect(save_related_session)
user_logged_out.connect(delete_related_session)


class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name='Question')
    answer = models.TextField(verbose_name='Answer',
                              help_text='Answers allow use of HTML')
    is_visible = models.BooleanField(default=True, verbose_name='Is visible')

import datetime
import hashlib
import re

from bs4 import BeautifulSoup

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from myjobs.models import User
from myjobs.tests.factories import UserFactory
from myjobs.tests.setup import MyJobsBase
from myprofile.tests.factories import PrimaryNameFactory
from registration.forms import InvitationForm
from registration.models import ActivationProfile, Invitation
from registration.tests.factories import InvitationFactory
from seo.models import CompanyUser
from seo.tests import CompanyFactory


class RegistrationModelTests(MyJobsBase):
    """
    Test the model and manager used in the default backend.
    
    """
    user_info = {'password1': 'swordfish',
                 'email': 'alice@example.com',
                 'send_email': True}
    
    def setUp(self):
        super(RegistrationModelTests, self).setUp()
        self.old_activation = getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', None)
        settings.ACCOUNT_ACTIVATION_DAYS = 7

    def tearDown(self):
        super(RegistrationModelTests, self).tearDown()
        settings.ACCOUNT_ACTIVATION_DAYS = self.old_activation

    def test_profile_creation(self):
        """
        Creating a registration profile for a user populates the
        profile with the correct user and a SHA1 hash to use as
        activation key.
        
        """
        new_user, created = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        self.assertEqual(ActivationProfile.objects.count(), 1)
        self.assertEqual(profile.user.id, new_user.id)
        self.failUnless(re.match('^[a-f0-9]{40}$', profile.activation_key))
        self.assertEqual(unicode(profile),
                         "Registration for alice@example.com")

    def test_user_creation_email(self):
        """
        By default, creating a new user sends an activation email.
        
        """
        User.objects.create_user(**self.user_info)
        self.assertEqual(len(mail.outbox), 1)

    def test_user_creation_no_email(self):
        """
        Passing ``send_email=False`` when creating a new user will not
        send an activation email.
        
        """
        self.user_info['send_email'] = False
        User.objects.create_user(
            site=Site.objects.get_current(),
            **self.user_info)
        self.assertEqual(len(mail.outbox), 0)

    def test_unexpired_account(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``False``
        within the activation window.
        
        """
        new_user, _ = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        self.failIf(profile.activation_key_expired())

    def test_expired_account(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``True``
        outside the activation window.
        
        """
        new_user, created = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        profile.sent -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        profile.save()
        self.failUnless(profile.activation_key_expired())

    def test_valid_activation(self):
        """
        Activating a user within the permitted window makes the
        account active, and resets the activation key.
        
        """
        new_user, created = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        activated = ActivationProfile.objects.activate_user(profile.activation_key)

        self.failUnless(isinstance(activated, User))
        self.assertEqual(activated.id, new_user.id)
        self.failUnless(activated.is_active)
        self.failUnless(activated.is_verified)

        profile = ActivationProfile.objects.get(user=new_user)
        self.assertEqual(profile.activation_key, ActivationProfile.ACTIVATED)

    def test_expired_activation(self):
        """
        Attempting to activate outside the permitted window does not
        activate the account.
        
        """
        new_user, created = User.objects.create_user(**self.user_info)

        profile = ActivationProfile.objects.get(user=new_user)
        profile.sent -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        profile.save()
        activated = ActivationProfile.objects.activate_user(profile.activation_key)

        self.failIf(isinstance(activated, User))
        self.failIf(activated)

        new_user = User.objects.get(email='alice@example.com')
        self.failIf(new_user.is_verified)

        profile = ActivationProfile.objects.get(user=new_user)
        self.assertNotEqual(profile.activation_key, ActivationProfile.ACTIVATED)

    def test_activation_invalid_key(self):
        """
        Attempting to activate with a key which is not a SHA1 hash
        fails.
        
        """
        self.failIf(ActivationProfile.objects.activate_user('foo'))

    def test_activation_already_activated(self):
        """
        Attempting to re-activate an already-activated account fails.
        
        """
        new_user, created = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        ActivationProfile.objects.activate_user(profile.activation_key)

        profile = ActivationProfile.objects.get(user=new_user)
        self.failIf(ActivationProfile.objects.activate_user(profile.activation_key))

    def test_activation_nonexistent_key(self):
        """
        Attempting to activate with a non-existent key (i.e., one not
        associated with any account) fails.
        
        """
        # Due to the way activation keys are constructed during
        # registration, this will never be a valid key.
        invalid_key = hashlib.sha1('foo').hexdigest()
        self.failIf(ActivationProfile.objects.activate_user(invalid_key))

    def test_expired_user_deletion(self):
        """
        ``RegistrationProfile.objects.delete_expired_users()`` only
        deletes inactive users whose activation window has expired.
        
        """
        User.objects.create_user(**self.user_info)
        expired_user, created = User.objects.create_user(
            password1='5UuYquA@', email='bob@example.com')

        profile = ActivationProfile.objects.get(user=expired_user)
        profile.sent -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS + 1)
        profile.save()

        ActivationProfile.objects.delete_expired_users()
        self.assertEqual(ActivationProfile.objects.count(), 1)
        self.assertRaises(User.DoesNotExist, User.objects.get, email='bob@example.com')

    def test_reset_activation(self):
        """
        Calling the reset_activation method on the ActivationProfile model
        generates a new activation key, even if it was already activated.
        """
        
        new_user, created = User.objects.create_user(**self.user_info)
        profile = ActivationProfile.objects.get(user=new_user)
        ActivationProfile.objects.activate_user(profile.activation_key)
        profile = ActivationProfile.objects.get(user=new_user)
        self.assertEqual(profile.activation_key, 'ALREADY ACTIVATED')
        profile.reset_activation()
        self.assertNotEqual(profile.activation_key, 'ALREADY ACTIVATED')

    def test_reactivate_disabled_user(self):
        for time in [datetime.timedelta(days=0),
                     datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)]:
            new_user, created = User.objects.create_user(**self.user_info)
            new_user.date_joined -= time
            new_user.disable()
            profile = ActivationProfile.objects.get(user=new_user)

            activated = ActivationProfile.objects.activate_user(profile.activation_key)

            self.failUnless(isinstance(activated, User))
            self.assertEqual(activated.id, new_user.id)
            self.failUnless(activated.is_active)

            profile = ActivationProfile.objects.get(user=new_user)
            self.assertEqual(profile.activation_key, ActivationProfile.ACTIVATED)


class InvitationModelTests(MyJobsBase):
    def setUp(self):
        super(InvitationModelTests, self).setUp()
        self.admin = UserFactory(is_superuser=True, is_staff=True,
                                 password='pass')
        self.client.login(username=self.admin.email,
                          password='pass')

    def test_invitation_admin_cant_edit(self):
        """
        Ensures that there is no way to edit an invitation once it is sent
        """
        invitation = InvitationFactory()
        resp = self.client.get(reverse(
            'admin:registration_invitation_changelist'))
        contents = BeautifulSoup(resp.content)

        # We can't edit items via action dropdown.
        bulk_options = contents.select('select[name=action]')[0]
        for action in bulk_options.select('option'):
            self.assertNotEqual('edit_selected', action.attrs['value'])

        # We can't click on the first data cell of a table row to edit.
        # td 0 is a checkbox. td 1 would normally contain the first field
        # to be shown as well as an edit link.
        edit_link = contents.select('td')[1]
        self.assertEqual(edit_link.text, invitation.invitee_email)
        self.assertEqual(edit_link.select('a'), [])

        resp = self.client.get(reverse(
            'admin:registration_invitation_change', args=[invitation.pk]))
        # We can't guess edit links.
        self.assertTrue(resp['Location'].endswith(
            reverse('admin:registration_invitation_changelist')))

    def test_invitation_admin_default_inviting_user(self):
        """
        When creating an invitation via the admin, the inviting user should
        default to the administrative user currently logged in
        """
        self.client.post(reverse(
            'admin:registration_invitation_add'),
            {'invitee_email': 'email@example.com'})
        invitation = Invitation.objects.get()
        self.assertEqual(invitation.inviting_user, self.admin)

    def test_invitation_form_creates_invitee(self):
        """
        When an invitation is created, set the invitee to the current owner
        of the email address used or create a new user if one does not exist
        """
        data = {
            'inviting_user': self.admin
        }
        User.objects.create_user(email='email@example.com', send_email=False)
        users = []
        for email in ['email@example.com', 'email2@example.com']:
            data['invitee_email'] = email
            form = InvitationForm(data)
            self.assertTrue(form.is_valid())
            invitation = form.save()
            user = User.objects.get_email_owner(email)
            users.append(user)

            self.assertIsNotNone(invitation.invitee)
            self.assertEqual(invitation.invitee_email, email)

            # Users created with invitations should receive an invitation
            # but not a normal user creation email
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox.pop()
            self.assertTrue('reserved' in email.body)

        self.assertEqual(len(users), 2)
        self.assertItemsEqual(users, set(users))

    def test_invitation_model_save_success(self):
        self.assertEqual(User.objects.count(), 1)
        for args in [{'invitee_email': self.admin.email},
                     {'invitee': self.admin},
                     {'invitee_email': 'new_user@example.com'}]:
            args.update({'inviting_user': self.admin})
            Invitation(**args).save()
        self.assertEqual(User.objects.count(), 2)

    def test_invitation_model_save_failure(self):
        """
        When we try to create an invitation with no invitee or we provide a
        mismatched User instance and email address, we should raise an
        exception
        """
        for args, exception_text in [({'invitee_email': 'new_user@example.com',
                                       'invitee': self.admin},
                                      'Invitee information does not match'),
                                     ({}, 'Invitee not provided')]:
            with self.assertRaises(ValidationError) as e:
                Invitation(**args).save()
            self.assertEqual(e.exception.messages, [exception_text])

    def test_invitation_emails_existing_user(self):
        company = CompanyFactory()
        user = UserFactory(email='companyuser@company.com',
                           is_verified=False)

        self.assertEqual(len(mail.outbox), 0)
        self.client.post(reverse('admin:seo_companyuser_add'),
                         {'user': user.pk,
                          'company': company.pk})
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox.pop()
        self.assertTrue('invitation' in email.subject)
        self.assertEqual(email.from_email, 'accounts@my.jobs')
        self.assertTrue(self.admin.email in email.body)
        self.assertTrue(company.name in email.body)

        ap = ActivationProfile.objects.get(email=user.email)

        body = BeautifulSoup(email.body)
        self.assertEqual(len(body.select('a')), 1)
        activation_href = body.select('a')[0].attrs['href']
        activation_href = activation_href.replace('https://secure.my.jobs', '')
        self.assertEqual(activation_href.split('?')[0],
                         reverse('invitation_activate',
                                 args=[ap.activation_key]))

        self.client.logout()
        self.client.get(activation_href)

        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.is_verified)

    def test_invitation_emails_new_user(self):
        self.assertEqual(len(mail.outbox), 0)
        Invitation(invitee_email='prm_user@company.com',
                   inviting_user=self.admin).save()
        self.assertEqual(len(mail.outbox), 1)

        user = User.objects.get(email='prm_user@company.com')
        self.assertTrue(user.in_reserve)
        self.assertFalse(user.is_verified)
        email = mail.outbox.pop()
        self.assertTrue('invitation' in email.subject)
        self.assertEqual(email.from_email, 'accounts@my.jobs')
        self.assertTrue(self.admin.email in email.body)

        ap = ActivationProfile.objects.get(email=user.email)

        body = BeautifulSoup(email.body)
        activation_href = body.select('a')[0].attrs['href']
        activation_href = activation_href.replace('https://secure.my.jobs', '')
        self.assertEqual(activation_href.split('?')[0],
                         reverse('invitation_activate',
                                 args=[ap.activation_key]))

        self.client.logout()
        response = self.client.get(activation_href)
        self.assertTrue('Your temporary password is ' in response.content)

        user = User.objects.get(pk=user.pk)
        self.assertFalse(user.in_reserve)
        self.assertTrue(user.is_verified)

    def test_invitation_email_with_name(self):
        PrimaryNameFactory(user=self.admin)

        Invitation(invitee_email='prm_user@company.com',
                   inviting_user=self.admin).save()

        email = mail.outbox.pop()
        self.assertTrue(self.admin.get_full_name() in email.body)

from django.forms import *
from django.core.validators import ValidationError
from django.utils.translation import ugettext_lazy as _

from myjobs.models import User
from myprofile.models import Name, SecondaryEmail


def make_choices(user, default_value='', default_text=''):
    """
    Turns the set of email addresses associated with a user into a list
    suitable for use in a ChoiceField

    Inputs:
    :user: User instance
    :default_value: Optional; What will be stored in the database
    :default_name: Optional; What will be displayed in place of :default_value:
        on forms
    """
    choices = []
    if default_value and default_text:
        choices.append((default_value, default_text))
    if user.is_active:
        choices.append((user.email, user.email))
        for email in SecondaryEmail.objects.filter(user=user, verified=True):
            choices.append((email.email, email.email))
    return choices


class BaseUserForm(ModelForm):
    """
    Most models in the other apps are associated with a user. This base form
    will take a user object as a key word argument and saves the form instance
    to a that specified user. It also takes a few common inputs that can be
    used to customize form rendering.

    Inputs (these are the common inputs we will use for rendering forms):
    :user: a user object. We will always pass a user object in  because all
        ProfileUnits are linked to a user.
    :auto_id: this is a boolean that determines whether a label is displayed or
        not and is by default set to True. Setting this to false uses the
        placeholder text instead, except for boolean and select fields.
    :empty_permitted: allow form to be submitted as empty even if the fields
        are required. This is particularly useful when we combine multiple
        Django forms on the front end and submit it as one request instead of
        several separate requests.
    :only_show_required: Template uses this flag to determine if it should only
        render required forms. Default is False.
    """

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.only_show_required = kwargs.pop('only_show_required', False)
        super(BaseUserForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(BaseUserForm, self).save(commit=False)
        if self.user and not self.user.is_anonymous():
            instance.user = self.user
            return instance.save()


class EditAccountForm(Form):
    given_name = CharField(label=_("First Name"),
                           widget=TextInput(
                               attrs={'placeholder': 'First Name'}),
                           max_length=40, required=False)
    family_name = CharField(label=_("Last Name"),
                            widget=TextInput(
                                attrs={'placeholder': 'Last Name'}),
                            max_length=40, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.choices = make_choices(self.user, 'none', 'Do not use Gravatar')
        super(EditAccountForm, self).__init__(*args, **kwargs)
        self.fields["gravatar"] = ChoiceField(
            label=_("Gravatar Email"),
            widget=Select(attrs={'id': 'id_gravatar'}),
            choices=self.choices,
            initial=self.choices[0][0])

    def clean(self):
        cleaned_data = super(EditAccountForm, self).clean()
        first = cleaned_data.get("given_name")
        last = cleaned_data.get("family_name")

        # Exclusive or. These fields must either both exist or not at all
        if bool(first) != bool(last):
            error_msg = u"Both a first and last name required."
            self._errors["given_name"] = self.error_class([error_msg])
            self._errors["family_name"] = self.error_class([error_msg])

            # These fields are no longer valid. Remove them from the
            # cleaned data.
            del cleaned_data["given_name"]
            del cleaned_data["family_name"]

        return cleaned_data

    def save(self, u):
        first = self.cleaned_data.get("given_name", None)
        last = self.cleaned_data.get("family_name", None)

        try:
            obj = Name.objects.get(user=u, primary=True)
            if not first and not last:
                obj.delete()
            else:
                obj.given_name = first
                obj.family_name = last
                obj.save()
        except Name.DoesNotExist:
            obj = Name(user=u, primary=True, given_name=first,
                       family_name=last)
            obj.save()

        u.gravatar = self.cleaned_data["gravatar"]
        u.save()


class EditCommunicationForm(BaseUserForm):
    def __init__(self, *args, **kwargs):
        super(EditCommunicationForm, self).__init__(*args, **kwargs)
        choices = make_choices(self.user)
        self.fields["email"] = ChoiceField(widget=Select(attrs={
                                           'id': 'id_digest_email'}),
                                           choices=choices,
                                           initial=choices[0][0])
        self.fields["email"].label = "Primary Email:"

    def save(self):
        if self.cleaned_data['email'] != self.user.email:
            new_email = SecondaryEmail.objects.get(
                email__iexact=self.cleaned_data['email'])
            if new_email.verified:
                new_email.set_as_primary()
            else:
                self.cleaned_data['email'] = self.user.email
        super(EditCommunicationForm, self).save(self)

    class Meta:
        model = User
        fields = ('email', 'opt_in_myjobs', 'opt_in_employers')


class ChangePasswordForm(Form):
    password = CharField(label="Password",
                         widget=PasswordInput(
                             attrs={'placeholder': 'Password'}))
    new_password1 = CharField(label="New Password",
                              widget=PasswordInput(
                                  attrs={'placeholder': 'New Password'}))
    new_password2 = CharField(label="New Password (again)",
                              widget=PasswordInput(
                                  attrs={'placeholder':
                                         'New Password (again)'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise ValidationError(("Wrong password."))
        else:
            return self.cleaned_data['password']

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        if 'new_password1' in self.cleaned_data and 'new_password2' in self.cleaned_data:
            if self.cleaned_data['new_password1'] != self.cleaned_data['new_password2']:
                error_msg = u"The new password fields did not match."
                self._errors["new_password1"] = self.error_class([error_msg])
                self._errors["new_password2"] = self.error_class([error_msg])

                # These fields are no longer valid. Remove them from the
                # cleaned data.
                del cleaned_data["new_password1"]
                del cleaned_data["new_password2"]
            else:
                return self.cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()


class UserAdminForm(ModelForm):
    class Meta:
        model = User

    # Used to update/change a password.
    new_password = CharField(label='New password', required=False)

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)

    def full_clean(self):
        """
        Removes ValidationErrors from gravatars that are actually correct.

        """
        super(UserAdminForm, self).full_clean()
        if 'gravatar' in self._errors:
            # If the gravatar is none (the default value) or blank, force
            # the ValidationError to be ignored.
            gravatar_val = self.data['gravatar']
            if gravatar_val == '' or gravatar_val == 'none':
                del self._errors['gravatar']

    def save(self, commit=True):
        instance = super(UserAdminForm, self).save(commit)
        # A blank string and 'none' are both valid gravatar options that
        # don't pass form validation, so gravatar needs to be saved here
        # if the gravatar was set to either.
        if (self.data['gravatar'] != instance.gravatar) and \
           (self.data['gravatar'] == 'none' or self.data['gravatar'] == ''):
            instance.gravatar = self.data['gravatar']
            instance.save()
        if not instance.user_guid:
            instance.make_guid()
        if 'new_password' in self.cleaned_data:
            if self.cleaned_data['new_password'] != '':
                instance.set_password(self.cleaned_data['new_password'])
                instance.save()
        return instance
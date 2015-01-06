from django.forms import (BooleanField, CharField, CheckboxInput, ChoiceField,
                          HiddenInput, ModelForm, RadioSelect, Select,
                          TextInput, Textarea, URLField, ValidationError)
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from myjobs.models import User
from myjobs.forms import BaseUserForm, make_choices
from mysearches.helpers import validate_dotjobs_url
from mysearches.models import (SavedSearch, SavedSearchDigest,
                               PartnerSavedSearch)
from mypartners.forms import PartnerEmailChoices
from mypartners.models import Contact, ADDITION, CHANGE
from registration.models import Invitation
from mypartners.helpers import (log_change, send_custom_activation_email,
                                tag_get_or_create)


class HorizontalRadioRenderer(RadioSelect.renderer):
    """
    Overrides the original RadioSelect renderer. The original displayed the
    radio buttons as an unordered list. This removes the unordered list,
    displaying just the radio button fields.
    """
    def render(self):
            return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class SavedSearchForm(BaseUserForm):
    def __init__(self, *args, **kwargs):
        super(SavedSearchForm, self).__init__(*args, **kwargs)
        choices = make_choices(self.user)
        self.fields["email"] = ChoiceField(widget=Select(), choices=choices,
                                           initial=choices[0][0])
    feed = URLField(widget=HiddenInput())
    notes = CharField(label=_("Notes and Comments"),
                      widget=Textarea(
                          attrs={'placeholder': 'Comments'}),
                      required=False)

    # day_of_week and day_of_month are not required in the database.
    # These clean functions ensure that it is required only when
    # the correct frequency is selected
    def clean_day_of_week(self):
        if self.cleaned_data.get('frequency', None) == 'W':
            if not self.cleaned_data['day_of_week']:
                raise ValidationError(_("This field is required."))
        return self.cleaned_data['day_of_week']

    def clean_day_of_month(self):
        if self.cleaned_data.get('frequency', None) == 'M':
            if not self.cleaned_data['day_of_month']:
                raise ValidationError(_("This field is required."))
        return self.cleaned_data['day_of_month']

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        feed = validate_dotjobs_url(url, self.user)[1]
        if feed:
            cleaned_data['feed'] = feed
            self._errors.pop('feed', None)
        else:
            error_msg = "That URL does not contain feed information"
            self._errors.setdefault('url', []).append(error_msg)

        self.cleaned_data['feed'] = feed
        return cleaned_data

    def clean_url(self):
        rss_url = validate_dotjobs_url(self.cleaned_data['url'], self.user)[1]
        if not rss_url:
            raise ValidationError(_('This URL is not valid.'))

        # Check if form is editing existing instance and if duplicates exist
        if not self.instance.pk and SavedSearch.objects.filter(user=self.user,
                                                               url=self.cleaned_data['url']):
            raise ValidationError(_('URL must be unique.'))
        return self.cleaned_data['url']

    def save(self, commit=True):
        self.instance.feed = self.cleaned_data['feed']
        return super(SavedSearchForm, self).save(commit)

    class Meta:
        model = SavedSearch
        widgets = {
            'notes': Textarea(attrs={'rows': 5, 'cols': 24}),
            'sort_by': RadioSelect(renderer=HorizontalRadioRenderer)
        }

class DigestForm(BaseUserForm):
    def __init__(self, *args, **kwargs):
        super(DigestForm, self).__init__(*args, **kwargs)
        choices = make_choices(self.user)
        self.fields["email"] = ChoiceField(widget=Select(attrs={
                                           'id': 'id_digest_email'}),
                                           choices=choices,
                                           initial=choices[0][0],
                                           label=_('Send digest results to:'))

    is_active = BooleanField(label=_('Send as a digest:'),
                             widget=CheckboxInput(attrs={'id':'id_digest_active'}),
                             required=False)

    def clean_day_of_week(self):
        if self.cleaned_data.get('frequency', None) == 'W':
            if not self.cleaned_data['day_of_week']:
                raise ValidationError(_("This field is required."))
        return self.cleaned_data['day_of_week']

    def clean_day_of_month(self):
        if self.cleaned_data.get('frequency', None) == 'M':
            if not self.cleaned_data['day_of_month']:
                raise ValidationError(_("This field is required."))
        return self.cleaned_data['day_of_month']

    class Meta:
        model = SavedSearchDigest


class PartnerSavedSearchForm(ModelForm):
    def __init__(self, *args, **kwargs):
        choices = PartnerEmailChoices(kwargs.pop('partner', None))
        super(PartnerSavedSearchForm, self).__init__(*args, **kwargs)
        self.fields["email"] = ChoiceField(
            widget=Select(), choices=choices,
            initial=choices[0][0], label="Send Results to",
            help_text="If a contact does not have an email they will "
                      "not show up on this list.")
        self.fields["notes"].label = "Notes and Comments"
        self.fields["url_extras"].label = "Source Codes & Campaigns"
        if self.instance.id and self.instance.tags:
            tag_names = ",".join([tag.name for tag in self.instance.tags.all()])
            self.initial['tags'] = tag_names
        self.fields['tags'] = CharField(
            label='Tags', max_length=255, required=False,
            widget=TextInput(attrs={'id': 'p-tags', 'placeholder': 'Tags'})
        )

        initial = kwargs.get("instance")
        feed_args = {"widget": HiddenInput()}
        if initial:
            feed_args["initial"] = initial.feed
        self.fields["feed"] = URLField(**feed_args)

    class Meta:
        model = PartnerSavedSearch
        fields = ('label', 'url', 'url_extras', 'is_active', 'email',
                'account_activation_message', 'frequency', 'day_of_month',
                'day_of_week', 'jobs_per_email', 'notes')
        exclude = ('provider', 'sort_by', )
        widgets = {
            'notes': Textarea(attrs={'rows': 5, 'cols': 24}),
            'url_extras': TextInput(attrs={
                'placeholder': 'src=1234&q=manager'})
        }

    def clean_day_of_week(self):
        if self.cleaned_data.get('frequency', None) == 'W':
            if not self.cleaned_data['day_of_week']:
                raise ValidationError(_("This field is required."))
        return self.cleaned_data['day_of_week']

    def clean_day_of_month(self):
        if self.cleaned_data.get('frequency', None) == 'M':
            if not self.cleaned_data['day_of_month']:
                raise ValidationError(_("This field is required."))
        return self.cleaned_data['day_of_month']

    def clean_tags(self):
        data = filter(bool, self.cleaned_data['tags'].split(','))
        tags = tag_get_or_create(self.data.get('company'), data)
        return tags

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')
        user_email = cleaned_data.get('email')

        if not user_email:
            raise ValidationError(_("This field is required."))

        # Get or create the user since they might not exist yet
        created = False
        user = User.objects.get_email_owner(email=user_email)
        if user is None:
            # Don't send an email here, as this is not a typical user creation.
            user, created = User.objects.create_user(email=user_email,
                                                     send_email=False,
                                                     in_reserve=True)
            self.instance.user = user
            Contact.objects.filter(email=user_email).update(user=user)
        else:
            self.instance.user = user

        setattr(self, 'created', created)

        feed = validate_dotjobs_url(url, user)[1]
        if feed:
            cleaned_data['feed'] = feed
            self._errors.pop('feed', None)
        else:
            error_msg = "That URL does not contain feed information"
            self._errors.setdefault('url', []).append(error_msg)

        self.cleaned_data['feed'] = feed
        return cleaned_data

    def save(self, commit=True):
        self.instance.feed = self.cleaned_data.get('feed')
        is_new_or_change = CHANGE if self.instance.pk else ADDITION
        instance = super(PartnerSavedSearchForm, self).save(commit)
        tags = self.cleaned_data.get('tags')
        self.instance.tags = tags
        if is_new_or_change == ADDITION:
            invite_args = {
                'invitee_email': instance.email,
                'invitee': instance.user,
                'inviting_user': instance.created_by,
                'inviting_company': instance.partner.owner,
                'added_saved_search': instance,
            }
            Invitation(**invite_args).save()
        partner = instance.partner
        contact = Contact.objects.filter(partner=partner,
                                         user=instance.user)[0]
        log_change(instance, self, instance.created_by, partner,
                   contact.email, action_type=is_new_or_change)

        return instance


class PartnerSubSavedSearchForm(ModelForm):
    class Meta:
        model = PartnerSavedSearch
        fields = ('sort_by', 'frequency', 'day_of_month', 'day_of_week')
        exclude = ('provider', 'url_extras', 'partner_message',
                   'account_activation_message', 'created_by', 'user',
                   'created_on', 'label', 'url', 'feed', 'email', 'notes',
                   'tags', )
        widgets = {
            'sort_by': RadioSelect(renderer=HorizontalRadioRenderer,
                                   attrs={'id': 'sort_by'}),
            'frequency': Select(attrs={'id': 'frequency'}),
            'day_of_month': Select(attrs={'id': 'day_of_month'}),
            'day_of_week': Select(attrs={'id': 'day_of_week'})
        }

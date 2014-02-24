from django import forms
from django.contrib.admin.models import ADDITION, CHANGE
from django.core.exceptions import ValidationError
from django.forms.util import ErrorList
from django.utils.safestring import mark_safe

from collections import OrderedDict

from myprofile.forms import generate_custom_widgets
from myjobs.forms import BaseUserForm
from mypartners.models import (Contact, Partner, ContactRecord, PRMAttachment,
                               MAX_ATTACHMENT_MB)
from mypartners.helpers import log_change
from mypartners.widgets import (MultipleFileField, MultipleFileInputWidget,
                                SplitDateTimeDropDownField, TimeDropDownField)


class ContactForm(forms.ModelForm):
    """
    Creates a new contact or edits an existing one.
    """
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(
            label="Name", max_length=255, required=True,
            widget=forms.TextInput(attrs={'placeholder': 'Full Name',
                                          'id': 'id_contact-name'}))

    class Meta:
        form_name = "Contact Information"
        model = Contact
        exclude = ['user']
        widgets = generate_custom_widgets(model)
        widgets['notes'] = forms.Textarea(
            attrs={'rows': 5, 'cols': 24,
                   'placeholder': 'Notes About This Contact'})

    def save(self, user, commit=True):
        is_new = CHANGE if self.instance.pk else ADDITION
        partner = Partner.objects.get(id=self.data['partner'])
        contact = self.instance
        contact.save()

        partner.add_contact(contact)
        partner.save()

        log_change(contact, self, user, partner, contact.name,
                   action_type=is_new)

        return contact



class PartnerInitialForm(BaseUserForm):
    """
    This form is used when an employer currently has no partner to create a
    partner (short and sweet version).
    """
    def __init__(self, *args, **kwargs):
        super(PartnerInitialForm, self).__init__(*args, **kwargs)
        self.fields['pc-contactname'] = forms.CharField(
            label="Primary Contact Name", max_length=255, required=False,
            widget=forms.TextInput(
                attrs={'placeholder': 'Primary Contact Name'}))
        self.fields['pc-contactemail'] = forms.EmailField(
            label="Primary Contact Email", max_length=255, required=False,
            widget=forms.TextInput(
                attrs={'placeholder': 'Primary Contact Email'}))

    class Meta:
        form_name = "Partner Information"
        model = Partner
        fields = ['name', 'uri']
        widgets = generate_custom_widgets(model)

    def save(self, user, commit=True):
        is_new = CHANGE if self.instance.pk else ADDITION
        company_id = self.data['company_id']
        self.instance.owner_id = company_id

        if self.data['pc-contactname'] or self.data['pc-contactemail']:
            if self.data['pc-contactname'] and self.data['pc-contactemail']:
                contact = Contact(name=self.data['pc-contactname'],
                                  email=self.data['pc-contactemail'])
            elif self.data['pc-contactname']:
                contact = Contact(name=self.data['pc-contactname'])
            else:
                contact = Contact(email=self.data['pc-contactemail'])
            contact.save()

            self.instance.primary_contact = contact
            self.instance.save()
            self.instance.add_contact(contact)

        log_change(self.instance, self, user, self.instance,
                   self.instance.name, action_type=is_new)

        self.instance.save()
        return self.instance


class NewPartnerForm(BaseUserForm):
    def __init__(self, *args, **kwargs):
        """
        This form is used only to create a partner.

        Had to change self.fields into an OrderDict to preserve order then
        'append' to the new fields because new fields need to be first.

        """
        super(NewPartnerForm, self).__init__(*args, **kwargs)
        for field in self.fields.itervalues():
            field.label = "Primary Contact " + field.label
        model_fields = OrderedDict(self.fields)

        new_fields = {
            'partnername': forms.CharField(
                label="Partner Organization", max_length=255, required=True,
                widget=forms.TextInput(
                    attrs={'placeholder': 'Partner Organization',
                           'id': 'id_partner-partnername'})),
            'partnerurl': forms.URLField(
                label="Partner URL", max_length=255, required=False,
                widget=forms.TextInput(attrs={'placeholder': 'Partner URL',
                                              'id': 'id_partner-partnerurl'}))
        }

        ordered_fields = OrderedDict(new_fields)
        ordered_fields.update(model_fields)
        self.fields = ordered_fields

    class Meta:
        form_name = "Partner Information"
        model = Contact
        exclude = ['user']
        widgets = generate_custom_widgets(model)
        widgets['notes'] = forms.Textarea(
            attrs={'rows': 5, 'cols': 24,
                   'placeholder': 'Notes About This Contact'})

    def save(self, user, commit=True):
        is_new = CHANGE if self.instance.pk else ADDITION
        company_id = self.data['company_id']
        owner_id = company_id
        if self.data['partnerurl']:
            partner = Partner(name=self.data['partnername'],
                              uri=self.data['partnerurl'], owner_id=owner_id)
            partner.save()
        else:
            partner = Partner(name=self.data['partnername'], owner_id=owner_id)
            partner.save()

        self.data = self.remove_partner_data(
            self.data, ['partnername', 'partnerurl', 'csrfmiddlewaretoken',
                        'company', 'company_id', 'ct'])

        has_data = False
        for value in self.data.itervalues():
            if value != ['']:
                if value == ['USA']:
                    continue
                has_data = True

        if has_data:
            self.instance.save()
            partner.add_contact(self.instance)
            partner.primary_contact_id = self.instance.id
            partner.save()

            log_change(self.instance, self, user, partner,
                       self.instance.name, action_type=is_new)


            return self.instance



    def remove_partner_data(self, dictionary, keys):
        new_dictionary = dict(dictionary)
        for key in keys:
            del new_dictionary[key]
        return new_dictionary


class PartnerForm(BaseUserForm):
    """
    This form is used only to edit the partner form. (see prm/view/details)

    """
    def __init__(self, *args, **kwargs):
        super(PartnerForm, self).__init__(*args, **kwargs)
        choices = [(contact.id, contact.name) for contact in
                   kwargs['instance'].contacts.all()]
        if kwargs['instance'].primary_contact:
            for choice in choices:
                if choice[0] == kwargs['instance'].primary_contact_id:
                    choices.insert(0, choices.pop(choices.index(choice)))
            if not kwargs['instance'].primary_contact:
                choices.insert(0, ('', "No Primary Contact"))
            else:
                choices.append(('', "No Primary Contact"))
        else:
            choices.insert(0, ('', "No Primary Contact"))
        self.fields['primary_contact'] = forms.ChoiceField(
            label="Primary Contact", required=False, initial=choices[0][0],
            choices=choices)

    class Meta:
        form_name = "Partner Information"
        model = Partner
        fields = ['name', 'uri']
        widgets = generate_custom_widgets(model)

    def save(self, user, commit=True):
        is_new = CHANGE if self.instance.pk else ADDITION
        self.instance.primary_contact_id = self.data['primary_contact']
        self.instance.save()

        log_change(self.instance, self, user, self.instance,
                   self.instance.name, action_type=is_new)

        return self.instance


def PartnerEmailChoices(partner):
    choices = [(None, '----------')]
    contacts = partner.contacts.all()
    for contact in contacts:
        if contact.user:
            choices.append((contact.user.email, contact.name))
        else:
            if contact.email:
                choices.append((contact.email, contact.name))
    return choices


class ContactRecordForm(forms.ModelForm):
    date_time = SplitDateTimeDropDownField(label='Date & Time')
    length = TimeDropDownField()
    attachment = MultipleFileField(required=False,
                                   help_text="Max file size %sMB" %
                                             MAX_ATTACHMENT_MB)

    class Meta:
        form_name = "Contact Record"
        fields = ('contact_type', 'contact_name',
                  'contact_email', 'contact_phone', 'location',
                  'length', 'subject', 'date_time', 'job_id',
                  'job_applications', 'job_interviews', 'job_hires',
                  'notes', 'attachment')
        model = ContactRecord

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner')
        instance = kwargs.get('instance')
        choices = [(c.id, c.name) for c in partner.contacts.all()]
        if not instance:
            choices.insert(0, (None, '----------'))
        else:
            index = [x[1] for x in choices].index(instance.contact_name)
            tup = choices[index]
            choices.pop(index)
            choices.insert(0, tup)
        super(ContactRecordForm, self).__init__(*args, **kwargs)
        self.fields["contact_name"] = forms.ChoiceField(
            widget=forms.Select(), choices=choices, label="Contact")
        if instance:
            attachments = PRMAttachment.objects.filter(contact_record=instance)
            if attachments:
                choices = [(a.pk, get_attachment_link(partner.owner.id,
                                                      partner.id, a.id,
                                                      a.attachment.name.split("/")[-1]))
                           for a in attachments]
                self.fields["attach_delete"] = forms.MultipleChoiceField(
                    required=False, choices=choices, label="Delete Files",
                    widget=forms.CheckboxSelectMultiple)

    def clean(self):
        contact_type = self.cleaned_data.get('contact_type', None)
        if contact_type == 'email' and not self.cleaned_data['contact_email']:
            self._errors['contact_email'] = ErrorList([""])
        elif contact_type == 'phone' and not self.cleaned_data['contact_phone']:
            self._errors['contact_phone'] = ErrorList([""])
        elif contact_type == 'facetoface' and not self.cleaned_data['location']:
            self._errors['location'] = ErrorList([""])
        elif contact_type == 'job' and not self.cleaned_data['job_id']:
            self._errors['job_id'] = ErrorList([""])
        return self.cleaned_data

    def clean_contact_name(self):
        contact_id = self.cleaned_data['contact_name']
        if contact_id == 'None' or not contact_id:
            raise ValidationError('required')
        try:
            return Contact.objects.get(id=int(contact_id))
        except Contact.DoesNotExist:
            raise ValidationError("Contact does not exist")

    def clean_attachment(self):
        attachments = self.cleaned_data.get('attachment', None)
        for attachment in attachments:
            if attachment and attachment.size > MAX_ATTACHMENT_MB * 1048576:
                raise ValidationError('File too large')
        return self.cleaned_data['attachment']

    def save(self, user, partner, commit=True):
        is_new = CHANGE if self.instance.pk else ADDITION
        self.instance.partner = partner
        instance = super(ContactRecordForm, self).save(commit)

        attachments = self.cleaned_data.get('attachment', None)
        for attachment in attachments:
            if attachment:
                prm_attachment = PRMAttachment(attachment=attachment,
                                               contact_record=self.instance)
                setattr(prm_attachment, 'partner', self.instance.partner)
                prm_attachment.save()

        attach_delete = self.cleaned_data.get('attach_delete', [])
        for attachment in attach_delete:
            PRMAttachment.objects.get(pk=attachment).delete()

        try:
            identifier = instance.contact_email if instance.contact_email \
                else instance.contact_phone if instance.contact_phone \
                else instance.contact_name
        except Contact.DoesNotExist:
            # This should only happen if the user is editing the ids in the drop
            # down list of contacts. Since it's too late for a validation error
            # the user can deal with the logging issues they created.
            identifier = "unknown contact"

        log_change(instance, self, user, partner, identifier,
                   action_type=is_new)

        return instance


def get_attachment_link(company_id, partner_id, attachment_id, attachment_name):
    url = '/prm/download?company=%s&partner=%s&id=%s' % (company_id,
                                                         partner_id,
                                                         attachment_id)

    html = "<a href='{url}' target='_blank'>{attachment_name}</a>"
    return mark_safe(html.format(url=url, attachment_name=attachment_name))


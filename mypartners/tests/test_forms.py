from django.core.urlresolvers import reverse
from myjobs.tests.factories import UserFactory
from mypartners.forms import ContactForm, ContactRecordForm
from mypartners.models import Contact
from mypartners.tests.factories import ContactFactory
from mypartners.tests.test_views import MyPartnersTestCase
from mysearches.tests.factories import PartnerSavedSearchFactory
from mysearches.forms import PartnerSavedSearchForm


class ContactFormTests(MyPartnersTestCase):
    def setUp(self):
        super(ContactFormTests, self).setUp()
        self.data = {}
        for field in Contact._meta.fields:
            self.data[field.attname] = getattr(self.contact, field.attname,
                                               None)
        self.data['partner'] = self.partner.pk
        self.data['user'] = self.contact.user.pk

    def test_disable_email_changing_for_existing_user(self):
        """
        You shouldn't be able to edit the email for contacts that have
        been attached to users.

        """
        self.data['email'] = 'not@thecontact.email'
        self.data['company_id'] = 1
        form = ContactForm(instance=self.contact, data=self.data)
        self.assertTrue(form.is_valid())
        form.save(self.staff_user, self.partner.pk)
        self.assertNotEqual(self.contact.email, self.data['email'])
        email_count = Contact.objects.filter(email=self.data['email']).count()
        self.assertEqual(email_count, 0)

    def test_input_sanitized(self):
        """
        Test that extra whitespace is stripped when saving the form. This works
        because ContactForm is a subclass of
        universal.form.NormalizedModelForm.
        """
        self.data['name'] = "                    John    Doe            "
        self.data['company_id'] = 1
        form = ContactForm(instance=self.contact, data=self.data)
        self.assertTrue(form.is_valid())
        form.save(self.staff_user, self.partner.pk)
        
        contact = Contact.objects.get(email=self.data['email'])
        self.assertEqual(contact.name, "John Doe")


class PartnerSavedSearchFormTests(MyPartnersTestCase):
    def test_partner_saved_search_form_from_instance(self):
        user = UserFactory(email='user@example.com')
        ContactFactory(user=user, partner=self.partner)
        partner_saved_search = PartnerSavedSearchFactory(
            created_by=self.staff_user, provider=self.company,
            partner=self.partner, user=user, notes='')
        response = self.client.get(reverse('partner_edit_search') +
                                   '?partner=%s&id=%s' % (
                                       self.partner.pk,
                                       partner_saved_search.pk))
        self.assertTrue(partner_saved_search.feed in response.content)


class ContactRecordFormTests(MyPartnersTestCase):
    def test_archived_contacts_not_shown(self):
        """Test that archived contacts aren't selectable."""

        form = ContactRecordForm(partner=self.partner)
        self.assertIn(self.contact, form.fields['contact'].queryset)

        self.contact.delete()
        form = ContactRecordForm(partner=self.partner)
        self.assertNotIn(self.contact, form.fields['contact'].queryset)

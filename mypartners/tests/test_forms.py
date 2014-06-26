from mypartners.forms import ContactForm
from mypartners.models import Contact
from mypartners.tests.test_views import MyPartnersTestCase


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
        form = ContactForm(instance=self.contact, data=self.data)
        self.assertTrue(form.is_valid())
        form.save(self.staff_user, self.partner.pk)
        self.assertNotEqual(self.contact.email, self.data['email'])
        email_count = Contact.objects.filter(email=self.data['email']).count()
        self.assertEqual(email_count, 0)

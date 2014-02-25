from os import path

from django.core.files import File
from django.test import TestCase

from myjobs.models import User
from myjobs.tests.factories import UserFactory
from mydashboard.tests.factories import CompanyFactory
from mypartners.tests.factories import PartnerFactory, ContactFactory
from mypartners.models import Partner, Contact, PRMAttachment


class MyPartnerTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.company.save()

        self.partner = PartnerFactory(owner=self.company)
        self.contact = ContactFactory()
        self.partner.save()
        self.contact.save()

    def test_contact_to_partner_relationship(self):
        """
        Tests adding a contact to partner's contacts list and tests
        primary_contact. Also tests if the contact gets deleted the partner
        stays and turns primary_contact to None.
        """
        self.partner.add_contact(self.contact)
        self.partner.save()
        self.assertEqual(1, len(self.partner.contacts.all()))

        self.partner.primary_contact = self.contact
        self.partner.save()
        self.assertIsNotNone(self.partner.primary_contact)

        # making sure contact is the contact obj vs a factory object.
        contact = Contact.objects.get(name=self.contact.name)
        contact.delete()

        partner = Partner.objects.get(name=self.partner.name)
        self.assertFalse(partner.contacts.all())
        self.assertIsNone(partner.primary_contact)

    def test_contact_user_relationship(self):
        """
        Tests adding a User to Contact. Then tests to make sure User cascading
        delete doesn't delete the Contact and instead turns Contact.user to
        None.
        """
        self.contact.user = UserFactory(email=self.contact.email)
        self.contact.save()

        self.assertIsNotNone(self.contact.user)
        self.assertEqual(self.contact.name, self.contact.__unicode__())

        user = User.objects.get(email=self.contact.email)
        user.delete()

        contact = Contact.objects.get(name=self.contact.name)
        self.assertIsNone(contact.user)

    def test_bad_filename(self):
        """
        Confirms that non-alphanumeric or underscore characters are being
        stripped from file names.

        """
        filename = path.join(path.abspath(path.dirname(__file__)), 'data',
                             'zz\\x80\\xff*file(copy)na.me.htm)_-)l')
        expected_filename = 'zzx80xfffilecopyname.htm_l'
        f = File(open(filename))
        prm_attachment = PRMAttachment(attachment=f)
        setattr(prm_attachment, 'partner', self.partner)
        prm_attachment.save()
        PRMAttachment.objects.get(attachment__contains=expected_filename)
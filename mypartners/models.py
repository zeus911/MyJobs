from django.db import models

from myjobs.models import User
from mydashboard.models import Company


class Contact(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, verbose_name='Full Name',
                            blank=True)
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
        super(Contact, self).save(*args, **kwargs)


class Partner(models.Model):
    """
    Object that this whole app is built around.
    """
    name = models.CharField(max_length=255,
                            verbose_name='Partner Organization')
    uri = models.URLField(verbose_name='Partner URL', blank=True)
    contacts = models.ManyToManyField(Contact, related_name="partners_set")
    primary_contact = models.ForeignKey(Contact, null=True,
                                        on_delete=models.SET_NULL)
    # owner is the Company that owns this partner.
    owner = models.ForeignKey(Company)

    def __unicode__(self):
        return self.name

    def add_contact(self, contact):
        self.contacts.add(contact)
